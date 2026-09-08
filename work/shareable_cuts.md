# Capstone Shareable Cuts

## 5-Minute Demo Outline

**0:00–0:45 — Question**  
The project asks whether simple, observable content signals can help prioritize which pages deserve human review for refresh or diagnosis.

**0:45–1:30 — Data & method**  
I worked with the approved anonymized FlyRank internship dataset. I used observable content/search signals, a client-grouped validation split, and a Logistic Regression model so the baseline stayed interpretable.

**1:30–2:30 — Baseline vs model**  
I compare the model with the Week-4 rule baseline on the same evaluation framing. The model is treated as decision support, not as proof that a page will decline.

**2:30–3:30 — One chart + result**  
The key result is the model's measured ranking/classification performance under the grouped split: Recall 77.17%, Precision 73.39%, F1 75.23%, ROC-AUC 0.838. These are observed evaluation results, not production guarantees.

**3:30–4:30 — Recommendation**  
Use the ranked output to prioritize human review: investigate high-risk pages, especially where visibility or freshness makes the review valuable. Do not automatically rewrite, delete, redirect, or publish content.

**4:30–5:00 — Limits**  
The dataset is anonymized and the label is an evaluation proxy where noted. Results are directional and decision-support only; future performance may differ.

## Social Post

I built a small, interpretable ML decision-support pipeline for content prioritization using the anonymized FlyRank internship dataset. Instead of optimizing for complexity, I compared a simple baseline with a Logistic Regression model under client-grouped validation and audited the features for leakage. The evaluated model reached 77.17% recall, 73.39% precision, 75.23% F1, and 0.838 ROC-AUC on the held-out grouped split. The important takeaway is not that the model "knows" which content will decline, but that a transparent ranking can help humans decide what deserves review first.

## Employer-Facing Summary

I built an interpretable ML decision-support pipeline on the anonymized FlyRank internship dataset to prioritize content for human review. I compared a simple Week-4 baseline with Logistic Regression using client-grouped validation and leakage checks. The evaluation showed 77.17% recall, 73.39% precision, 75.23% F1, and 0.838 ROC-AUC, with the results framed as measured and directional rather than production guarantees.
