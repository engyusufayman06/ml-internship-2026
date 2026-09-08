# Task Audit — FlyRank ML Internship 2026

Last reviewed: 2026-09-08

This file is a working QA checklist. A task is not called "verified" merely because code exists; notebook execution and outputs must be checked where the environment permits it.

| Task | Notebook / artifact | State | QA note |
|---|---|---|---|
| ML-02 | `w01_research_question.ipynb` | Complete — execution queued | Fixed a real bug: prose had been placed in a Python code cell and caused `SyntaxError`. Rebuilt the notebook with markdown prose and executable data checks. |
| ML-03 | `w02_ml_task_framing.ipynb` | Complete | Task type, target/proxy, metric, unit of analysis, leakage warning, and decision framing are present. Existing execution output is present. |
| ML-04 | `w03_data_contract.ipynb` | Complete, execution pending | Contract is written and includes exactly three checks, five pre-cutoff features, a deliberate leakage experiment, and a limitation. Full warehouse execution requires the approved Hugging Face token in Colab/Secrets. |
| ML-05 | `w03_feature_leakage_check.ipynb` | Complete — execution queued | Filled the previously empty stretch notebook with a real feature vector, preprocessing, leakage audit, and exclusions. |
| ML-06 | `w04_signal_audit.ipynb` | Complete — execution queued | Filled the previously empty stretch notebook with distributions, three signal tests, verdicts, and a flag-linked test. |
| ML-07 | `w04_baseline_score.ipynb` | Complete — execution queued | Rebuilt the notebook so the evaluation-only decline proxy is created explicitly, while the frozen rule never uses the label. Precision@20/50 and base rate are computed. |
| ML-08 | `w05_model.ipynb` | Complete — execution queued | Logistic Regression, client-grouped split, preprocessing, same-test-row baseline comparison, metrics, coefficients, and error analysis are implemented. |
| ML-09 | `w06_validation_audit.ipynb` | Complete — execution queued | Random vs client-grouped validation, leakage audit, failure examples, coefficients, and claim rewrite are implemented. |
| ML-10 | `w07_action_playbook.ipynb` | Executed | Existing executed output records grouped 80/20 results: recall 77.17%, precision 73.39%, F1 75.23%, ROC-AUC 0.8381. |
| ML-11 | `docs/index.html`, `submission/paper_url.txt` | Complete | Public research page exists with the canonical paper sections and the submission URL is populated. |
| ML-12 | `capstone.ipynb` closing cells | Complete — execution queued | Added a 5-minute demo outline, social-post cut, and employer-facing 3-sentence summary. |

## Automated verification

`.github/workflows/execute-work-notebooks.yml` now runs the local-data notebooks top-to-bottom with `nbconvert` and commits executed notebooks only after successful execution. The workflow intentionally excludes ML-04 because that notebook needs the gated warehouse/Hugging Face token.

## Important integrity rule

Do not replace missing metrics with guessed numbers. If a notebook cannot be executed because a gated dataset/token is unavailable, the limitation stays explicit and the task is not marked fully execution-verified until it is actually run.
