# Signing Score: A Bias-Adjusted Framework for Football Recruitment Analytics

MSc Data Science project (University of Birmingham), completed as a company project with
Nottingham Forest Football Club. This repository contains the analysis pipeline behind the
paper *"What Is a 'Perfect' Signing? A Bias-Adjusted Framework for Football Recruitment
Analytics."*

## Overview

The project builds and validates a "Signing Score" recruitment metric from StatsBomb's
On-Ball Value (OBV), cross-checks it against an independently constructed Expected Threat
(xT) model, tests six common recruitment beliefs under a pre-registered
discovery/confirmation design, and evaluates the resulting score against real transfer
outcomes. Full methodology, results, and appendices are in [`paper/main_1.pdf`](paper/main_1.pdf).

## Repository structure

```
.
├── notebooks/
│   ├── 01_data_foundation.ipynb          # Section III — identity matching, position/duration
│   │                                       reconstruction, versatility scoring, cross-league merge
│   ├── 02_value_framework.ipynb          # Section V — OBV construction, xT cross-validation,
│   │                                       defensive-activity metric, goalkeeper shrinkage
│   ├── 03_mythbusting.ipynb              # Section VI — the six recruitment-belief tests, FDR
│   │                                       correction, discovery/confirmation splitting
│   ├── 04_signing_score.ipynb            # Section VII — team-strength adjustment, shrinkage
│   │                                       selection, hierarchical Bayesian extension attempt
│   ├── 05_external_evaluation.ipynb      # Section IX — transfer-outcome, durability, and
│   │                                       team-aggregate evaluation
│   ├── 06_hierarchical_bayes_ext.ipynb   # Isolated hierarchical Bayesian refinement notebook
│   └── 07_subsampling_robustness.ipynb   # Isolated repeated sub-sampling robustness check
├── dashboard/
│   └── app.py                            # Streamlit dashboard (Section VIII) — Explorer,
│                                            Compare, Lookup, and Summary views
├── data/
│   └── README.md                         # Data sources and access notes (see below)
├── paper/
│   └── main_1.pdf                        # Full paper, including all appendices
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/GoswamiMeghana/signing-score-msc-project.git
cd signing-score-msc-project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:

```
pandas
pyarrow
scipy
statsmodels
pymc
arviz
streamlit
jupyter
```

## Running the pipeline

The notebooks are numbered in dependency order and should be run in sequence, since each
consumes the checkpointed Parquet output of the ones before it:

```bash
jupyter notebook notebooks/01_data_foundation.ipynb
# ... run 02 through 05 in order ...
```

Notebooks `06` and `07` are independent extensions and can be run any time after `04` and
`03` respectively — they write to separate checkpoint files and do not affect the core
pipeline's validated results.

To launch the dashboard once the pipeline has produced its checkpoint files:

```bash
streamlit run dashboard/app.py
```

## Data availability

Base event and results data is drawn from [StatsBomb's open data](https://github.com/statsbomb/open-data)
and public multi-league results/transfer records (see `data/README.md` for exact sources).
Two datasets used in this project — SecondSpectrum player-tracking data and the injuries
dataset — were provided under an NDA as part of the company project agreement with
Nottingham Forest Football Club. They are **not included** in this repository and never
will be: they are held in a private, access-controlled Wasabi object storage bucket
accessible only to the project team, and the relevant notebooks read directly from that
protected location at runtime rather than from any file committed here. The interactive
dashboard is similarly deployed internally for the club's own recruitment workflow and is
not publicly hosted; representative screenshots and a walkthrough are provided in the
paper's appendix instead.

## Citation

If referencing this work, please cite the accompanying paper (see `paper/main_1.pdf`).
