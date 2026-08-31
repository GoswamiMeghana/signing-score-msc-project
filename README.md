# What Is a "Perfect" Signing?
### A Bias-Adjusted Framework for Football Recruitment Analytics

MSc Data Science project, University of Birmingham — completed as a company project with
**Nottingham Forest Football Club (NFFC)**.

---

## Overview

Football clubs spend heavily on transfers, but the stats behind those decisions are often
raw and unadjusted — confounded by team strength, squad rotation, and small-sample noise.
This project builds and validates a **bias-adjusted player valuation metric ("Signing
Score")** using StatsBomb event data across five European leagues and three seasons
(2022–2025), and asks a simple question: can a data-driven framework identify a good
signing *before* the transfer happens, not just describe it afterward?

---

## What's in this repo

| File | What it does |
|---|---|
| `_1Data_Foundation.ipynb` | Builds and verifies the core data pipeline from raw StatsBomb event data |
| `_2Value_Framework.ipynb` | Validates On-Ball Value (OBV) against an independently-built Expected Threat (xT) model |
| `_3Mythbusting.ipynb` | Tests six common recruitment beliefs using a pre-registered discovery/confirmation split |
| `_4Bias_Adjusted_Scoring.ipynb` | Builds the Signing Score — team-strength adjustment, empirical Bayes shrinkage |
| `_5Evaluation.ipynb` | External validation: real transfer outcomes, injury records, team-level results |
| `_6Hierarchial_Bayesian_scoring_refinement.ipynb` | An attempted hierarchical Bayesian extension to shrinkage (honestly reported, not adopted) |
| `_7robustness_check.ipynb` | 100-fold repeated random sub-sampling validation on two borderline findings |
| `self_app.py` | Interactive Streamlit dashboard — explore, compare, and look up real transfers |
| `self_requirements.txt` | Python dependencies for the dashboard |

---

## Running the dashboard

```bash
pip install -r self_requirements.txt
streamlit run self_app.py
```

The dashboard reads from local data checkpoints, which are **not included in this
repository** (see Data Availability below).

---

## Data Availability

StatsBomb event data, the injuries dataset, and SecondSpectrum tracking data are used
under this project's data access agreements as part of the company project with
Nottingham Forest FC, and are **not publicly redistributable**. No data files, credentials,
or club-specific exports are included in this repository — see `.gitignore`.

---

## Author

Meghana Goswami · MSc Data Science · University of Birmingham
