# Capstone Report — Refresh / Content Opportunity Scoring

- **Author:** Yusuf Ayman
- **Lane:** Refresh / Content Opportunity Scoring
- **Repo:** https://github.com/engyusufayman06/ml-internship-2026
- **Random seed:** 42

## 0. Abstract

This project asks which content pages should receive human review first for a potential refresh or improvement. I use the FlyRank internship starter snapshot of 30,000 pseudonymized pages and treat `trend_direction == "down"` as an evaluation-only proxy when the explicit label column is absent. The learned method is Logistic Regression with leakage-safe preprocessing and a client-grouped 80/20 holdout. The capstone notebook computes recall, precision, F1, ROC-AUC, Precision@20, and Precision@50 and compares the model with a frozen transparent baseline on the same holdout. The output is a ranked decision-support queue for human investigation, not an automatic content-editing system.

## 1. Problem framing

The decision is **which pages deserve attention first**. The unit of analysis is one pseudonymized content page. A content/SEO reviewer acts on the ranked output by investigating, refreshing, expanding, monitoring, or leaving a page unchanged. False positives cost review time; false negatives can cause useful opportunities to be missed.

ML earns its place if multiple observable signals contain a pattern that is difficult to express with one hand-written rule.

## 2. Data safety

The starter snapshot contains 30,000 rows and 44 columns. `client_id` and `content_id` are identifiers/grouping keys only. `trend_direction`, `trend_pct`, and the decline label are never model features. Baseline-generated fields and derived convenience buckets are also excluded.

No client names, private URLs, or raw search queries are used in public outputs. The notebook is designed to show only pseudonymous IDs and aggregate metrics.

## 3. Baseline

The frozen baseline says: **prioritize a page when it is at least 180 days since its last update and has at least 3,000 impressions in 90 days**. The score is its 90-day impressions when selected and zero otherwise. Each row receives a reason code and action label.

The baseline is deliberately transparent and is evaluated on the same grouped holdout used by the model in the capstone notebook.

## 4. Model / analysis

The learned model is Logistic Regression. Numeric fields use median imputation, missingness indicators, and standardization. Categorical fields use most-frequent imputation and one-hot encoding. `class_weight="balanced"` is used because the target is not perfectly balanced.

The feature list excludes the target, target-source fields, identifiers, baseline outputs, and other fields that would encode the decision after the fact.

When the starter CSV lacks `is_declining_label`, the notebook constructs it from `trend_direction == "down"` solely for retrospective evaluation. This is explicitly a proxy and not a future production label.

## 5. Evaluation

The primary validation is a client-grouped 80/20 split using `GroupShuffleSplit`, seed 42. The grouped design prevents the same client from appearing in both training and test data.

The capstone notebook prints the model and baseline metrics on the same holdout and asserts zero client overlap. It also prints a confusion matrix and supports false-positive/false-negative analysis.

Primary metric: **Recall**, because the first operational priority is to avoid missing pages that may need attention. Precision, F1, ROC-AUC, and Precision@K are supporting measures.

## 6. Interpretation

The model's coefficients are associations within this dataset after preprocessing; they are not causal effects. A positive coefficient pushes the predicted decline probability upward, while a negative coefficient pushes it downward.

The main practical finding is not that one feature "causes" decline. It is that a combination of observable content and performance signals can be tested as a ranking signal, and that the model can be checked under a stricter client-grouped split.

## 7. Recommendation

Use the ranked queue as a **review triage tool**:

1. **Stale + visible:** review for refresh first.
2. **Fresh + high model score:** perform a content diagnostic; do not automatically rewrite.
3. **Stale + low visibility:** diagnose whether there is still a viable opportunity before spending refresh capacity.
4. **Recent + low score:** monitor rather than prioritizing immediate intervention.

Confidence should be expressed through measured validation performance and the evidence behind each recommendation, not through an assumption that a high score guarantees decline.

## 8. Reproducibility

From a fresh clone:

```bash
pip install -r requirements.txt
```

Then open and run `work/notebooks/capstone.ipynb` top-to-bottom. The analysis uses random seed **42** and writes `work/outputs/capstone_metrics.json` plus `work/outputs/capstone_ranked_queue.csv` locally. Generated CSV/JSON artifacts are not intended to be committed as datasets; the metrics receipt is safe to keep when it contains no private data.

The earlier task notebooks remain under `work/notebooks/` and document the progression from research question → task framing → data contract → leakage audit → signal audit → baseline → model → validation → action playbook.

## 9. Acknowledgments & data credit

Built on the FlyRank ML Internship dataset. Data credit: https://flyrank.ai

## Claims checklist

- **Observed/measured:** yes.
- **Directional/decision-support:** yes.
- **Causal:** no.
- **Prediction of Google's algorithm:** no.
- **Client-identifying details:** intentionally excluded.
