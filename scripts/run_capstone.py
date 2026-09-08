from pathlib import Path
import json
import os
import duckdb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
REL = "hf://datasets/FlyRank/internship-warehouse"
FACT = f"{REL}/fact_content_daily_performance"
FEB = f"read_parquet('{FACT}/month=2026-02/*.parquet')"
MAR = f"read_parquet('{FACT}/month=2026-03/*.parquet')"
OUT = Path("work/outputs")
OUT.mkdir(parents=True, exist_ok=True)

if not os.environ.get("HF_TOKEN"):
    raise RuntimeError("HF_TOKEN is required. Add it as a repository Actions secret.")

con = duckdb.connect()
con.execute("SET enable_progress_bar = false")
con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")
con.execute("INSTALL huggingface")
con.execute("LOAD huggingface")
con.execute("SET VARIABLE hf_token = ?", [os.environ["HF_TOKEN"]])
con.execute("CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN getvariable('hf_token'))")

# Contract checks on the February decision window.
grains = con.sql(f"""
SELECT COUNT(*) AS duplicate_keys FROM (
  SELECT client_hash_id, content_hash_id, report_date
  FROM {FEB}
  GROUP BY 1,2,3 HAVING COUNT(*) > 1
)
""").fetchone()[0]
window = con.sql(f"SELECT COUNT(*), MIN(report_date), MAX(report_date) FROM {FEB}").fetchone()
avail = con.sql(f"""
SELECT COUNT(*), COUNT(*) FILTER (WHERE gsc_data_available IS TRUE)
FROM {FEB}
""").fetchone()
assert grains == 0, "Duplicate February grain keys detected"

features = con.sql(f"""
SELECT client_hash_id, content_hash_id,
  SUM(gsc_impressions) FILTER (WHERE gsc_data_available IS TRUE) AS feb_impressions,
  SUM(gsc_clicks) FILTER (WHERE gsc_data_available IS TRUE) AS feb_clicks,
  100.0 * SUM(gsc_clicks) FILTER (WHERE gsc_data_available IS TRUE)
    / NULLIF(SUM(gsc_impressions) FILTER (WHERE gsc_data_available IS TRUE),0) AS feb_ctr,
  SUM(gsc_sum_position) FILTER (WHERE gsc_data_available IS TRUE)
    / NULLIF(SUM(gsc_impressions) FILTER (WHERE gsc_data_available IS TRUE),0) AS feb_avg_position,
  COUNT(*) FILTER (WHERE gsc_data_available IS TRUE) AS feb_measured_days
FROM {FEB}
GROUP BY 1,2
""").df()

labels = con.sql(f"""
SELECT client_hash_id, content_hash_id,
  SUM(gsc_clicks) FILTER (WHERE gsc_data_available IS TRUE) AS mar_clicks,
  COUNT(*) FILTER (WHERE gsc_data_available IS TRUE) AS mar_measured_days
FROM {MAR}
GROUP BY 1,2
HAVING COUNT(*) FILTER (WHERE gsc_data_available IS TRUE) > 0
""").df()
labels["went_dark"] = (labels["mar_clicks"] == 0).astype(int)

frame = features.merge(labels, on=["client_hash_id", "content_hash_id"], how="inner")
feature_cols = ["feb_impressions", "feb_clicks", "feb_ctr", "feb_avg_position", "feb_measured_days"]
assert not frame.empty, "No February-to-March evaluation rows were found"
assert frame[feature_cols].notna().any(axis=1).any(), "No usable feature rows"

# Client-grouped holdout: no client appears on both sides.
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=SEED)
train_idx, test_idx = next(gss.split(frame, groups=frame["client_hash_id"]))
train, test = frame.iloc[train_idx].copy(), frame.iloc[test_idx].copy()
assert set(train.client_hash_id).isdisjoint(set(test.client_hash_id))

X_train, X_test = train[feature_cols], test[feature_cols]
y_train, y_test = train["went_dark"], test["went_dark"]
model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED))
model.fit(X_train, y_train)
model_prob = model.predict_proba(X_test)[:, 1]
model_pred = (model_prob >= 0.50).astype(int)

baseline_flag = test["feb_measured_days"].fillna(0).ge(14) & test["feb_impressions"].fillna(0).ge(3000)
baseline_score = np.where(baseline_flag, test["feb_impressions"].fillna(0), 0.0)
baseline_pred = baseline_flag.astype(int)

def p_at_k(y, score, k):
    k = min(k, len(y))
    order = np.argsort(-np.asarray(score))[:k]
    return float(np.asarray(y)[order].mean())

def metrics(name, pred, score):
    return {
        "method": name,
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, score)),
        "precision_at_20": p_at_k(y_test, score, 20),
        "precision_at_50": p_at_k(y_test, score, 50),
    }

comparison = [metrics("February rule baseline", baseline_pred, baseline_score), metrics("Logistic Regression", model_pred, model_prob)]
model_row = comparison[1]
base_row = comparison[0]

# Full ranked queue. IDs are pseudonymous warehouse keys; no domains, queries, or client names are exported.
queue = test[["client_hash_id", "content_hash_id", "feb_impressions", "feb_measured_days", "went_dark"]].copy()
queue["model_score"] = model_prob
queue["baseline_flag"] = baseline_flag.astype(int)
queue["reason_code"] = np.select(
    [queue["baseline_flag"].eq(1) & queue["model_score"].ge(0.5), queue["model_score"].ge(0.5), queue["baseline_flag"].eq(1)],
    ["stale_visible_and_model_risk", "model_risk", "visible_review_rule"],
    default="monitor"
)
queue["recommended_action"] = queue["reason_code"].map({
    "stale_visible_and_model_risk": "refresh_review",
    "model_risk": "content_diagnostic",
    "visible_review_rule": "diagnostic_review",
    "monitor": "monitor",
})
queue = queue.sort_values(["model_score", "feb_impressions"], ascending=False).reset_index(drop=True)
queue.insert(0, "rank", np.arange(1, len(queue) + 1))
queue.to_csv(OUT / "capstone_ranked_queue.csv", index=False)

metrics_payload = {
    "dataset": "FlyRank/internship-warehouse",
    "feature_window": "2026-02",
    "outcome_window": "2026-03",
    "decision_cutoff": "2026-02-28",
    "grain_duplicate_keys": int(grains),
    "feb_row_count": int(window[0]),
    "feb_min_date": str(window[1]),
    "feb_max_date": str(window[2]),
    "feb_measured_rows": int(avail[1]),
    "evaluation_rows": int(len(frame)),
    "train_rows": int(len(train)),
    "test_rows": int(len(test)),
    "train_clients": int(train.client_hash_id.nunique()),
    "test_clients": int(test.client_hash_id.nunique()),
    "positive_rate": float(frame.went_dark.mean()),
    "model": "Logistic Regression",
    "features": feature_cols,
    "split": "client_grouped_80_20",
    "comparison": comparison,
    "model_confusion_matrix": confusion_matrix(y_test, model_pred).tolist(),
    "model_vs_baseline_recall_delta": float(model_row["recall"] - base_row["recall"]),
    "notes": [
        "went_dark is a March outcome and is never a February feature",
        "GSC unavailable rows are not treated as zero performance",
        "Results are observational decision support, not causal evidence about content refresh or Google's algorithm",
    ],
}
(OUT / "capstone_metrics.json").write_text(json.dumps(metrics_payload, indent=2))

# Compact public-safe summary for the paper; no raw warehouse rows.
summary = {
    "question": "Which content items should be prioritized for refresh review using signals available by the February 2026 cutoff?",
    "decision_cutoff": "2026-02-28",
    "outcome_window": "2026-03",
    "evaluation_rows": int(len(frame)),
    "model": model_row,
    "baseline": base_row,
    "recommendation_counts": queue["recommended_action"].value_counts().to_dict(),
}
(OUT / "paper_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
