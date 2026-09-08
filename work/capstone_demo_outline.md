# Capstone Showcase — 5-Minute Demo

## Case-study framing
The FlyRank content problem is prioritization: given many pieces of content, which ones should receive human attention first? This project tests whether observable signals can support that decision without pretending the model is an autonomous content editor.

## Demo flow
1. **Question (45 sec):** Can observable content/search signals help prioritize content for human review?
2. **Data (45 sec):** Approved anonymized FlyRank internship dataset; public-safe IDs and aggregate signals only.
3. **Method (60 sec):** Interpretable Logistic Regression, compared with the Week-4 rule baseline using the same evaluation framing and client-grouped validation.
4. **Chart (60 sec):** Show the model-vs-baseline result and explain what the metric measures.
5. **Honest result (60 sec):** Recall 77.17%, precision 73.39%, F1 75.23%, ROC-AUC 0.838 on the grouped evaluation. These are observed results, not a guarantee of future performance.
6. **Recommendation (30 sec):** Use the ranked queue to prioritize human investigation; do not auto-publish, delete, redirect, or rewrite content.
