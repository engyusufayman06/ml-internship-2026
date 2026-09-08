# Which Content Should Be Reviewed First?

## Abstract
This study asks how an SEO/content team can prioritize pages for human review when the objective is to surface potentially declining content without leaking future outcome information into the model. We define an evaluation target from the available FlyRank internship data and compare an interpretable logistic-regression ranking model with a simple stale-and-visible baseline. The workflow uses explicit temporal feature controls, client-grouped holdout validation, preprocessing for missing values and categorical variables, and ranking-oriented metrics including Precision@20 and Precision@50. The analysis is designed as decision support rather than an automatic refresh system, and reported relationships are observational rather than causal. The current repository contains the reproducible implementation and public-safe reporting artifact, while gated warehouse execution depends on the FlyRank Hugging Face access credential and is not represented by fabricated results.

## 1. Introduction / Problem Statement
Content teams cannot manually inspect every page with equal priority. The practical question is therefore: **which content should be reviewed first?** A useful system should surface potentially declining pages early, provide an interpretable reason for prioritization, and avoid turning a model score into an automatic publishing or deletion decision.

This project frames the task as decline-risk prioritization. The output is a ranked queue for human investigation.

## 2. Data
The project follows the FlyRank ML Internship warehouse contract. The full warehouse is gated and is accessed through DuckDB/Hugging Face in the reproducibility workflow. The decision/feature window is February 2026 and the outcome window is March 2026. The implementation uses content-level performance information while keeping client identifiers as grouping variables rather than predictive features.

Public reporting excludes client names, domains, private queries, URLs, credentials, and raw private exports. Pseudonymous identifiers may be retained only in machine-readable artifacts where required for reproducibility and are not presented as business identities.

### Exclusions
- Outcome and outcome-derived fields are excluded from model features.
- Content/client identifiers are excluded from predictive features.
- Any field computed from the future outcome window is excluded from the feature matrix.
- Baseline-derived scores and action labels are excluded from the model to prevent circular evaluation.
- Rows without the required measurement for an outcome are not silently treated as zero.

## 3. Methodology
### Research design
The model is evaluated with a client-grouped 80/20 holdout using a fixed random seed. Grouping prevents the same client from appearing in both training and test sets.

### Features
The full-warehouse runner constructs pre-outcome performance features from the February window, including impressions, clicks, CTR, average position, and measured-day information. Missing numeric values are imputed with medians and accompanied by missingness indicators. Categorical variables, when present, are imputed and one-hot encoded.

### Model
The primary model is balanced logistic regression. Its predicted probability is used as a ranking score. A 0.50 threshold is used for binary classification metrics, while Precision@20 and Precision@50 evaluate the usefulness of the top-ranked review queue.

### Baseline
The operational baseline is intentionally simple: identify sufficiently measured content that is both stale and visible. The rule uses age since update and recent impressions and is intended as a transparent human-review heuristic.

### Leakage controls
The target, target-derived trend fields, identifiers, future-window information, and baseline-derived fields are explicitly excluded. The grouped split is checked for zero client overlap.

## 4. Results
The repository contains two execution layers: starter-snapshot notebooks for the internship workflow and a full-warehouse runner for the final capstone. Starter-snapshot execution previously produced a client-grouped holdout result of 77.2% recall, 73.4% precision, 75.2% F1, and 0.838 ROC-AUC. These figures are explicitly labeled as starter-snapshot execution and are **not** presented as full-warehouse results.

The final full-warehouse workflow writes its measured metrics to `work/outputs/capstone_metrics.json` after successful authenticated execution. No full-warehouse metric is invented here when authenticated execution has not completed.

## 5. Interpretation
The appropriate interpretation is decision support. A higher score means that a page should be considered earlier in a human review queue under the learned associations. It does not mean that refreshing the page will necessarily improve search performance, nor does it establish a causal relationship with a search-engine algorithm change.

## 6. Ranked Recommendation Playbook
1. **High model risk + meaningful visibility:** prioritize a content diagnostic and refresh review.
2. **High model risk without strong visibility:** investigate whether the page has a viable search opportunity before investing in a refresh.
3. **Baseline-positive pages:** retain as a transparent review queue even when the model score is lower.
4. **Low-risk pages:** monitor rather than automatically changing content.
5. **All interventions:** require human review and measurement after the intervention.

## 7. Limitations & Honest Framing
- The model estimates associations, not causality.
- A single grouped holdout is not proof of universal generalization.
- Outcome construction depends on the warehouse measurement contract.
- Gated warehouse access is required for final full-release execution.
- Ranking quality depends on the review budget and the prevalence of true declines.
- Search performance can be affected by factors not represented in the available data.

## 8. Reproducibility
Repository: https://github.com/engyusufayman06/ml-internship-2026

Key artifacts:
- `work/notebooks/` — internship assignments and capstone notebook
- `scripts/run_capstone.py` — authenticated full-warehouse execution
- `.github/workflows/capstone-full-warehouse.yml` — reproducible CI execution
- `work/outputs/` — generated public-safe metrics and ranked queue
- `submission/paper_url.txt` — submission URL

## 9. Acknowledgments & Data Credit
Built on the FlyRank ML Internship dataset. FlyRank: https://flyrank.ai

This artifact is intended for educational research and decision-support purposes. It does not expose client identities or private search data and does not claim causal impact on Google Search or any other search engine.
