# CKD CDS prototype UI

Research decision-support demo (Rice-style **app.py** equivalent). **Not** for clinical use.

## Prerequisites

- Run notebook **`12B`** (or **`12B-Resume`**) so this file exists:
  - `outputs/supervisor_runs/step2_mimic_checkpoint.pkl`
- Optional (global SHAP tab): run **`15B`** → `step2_mimic_shap_top15.csv`

## Install UI dependency

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
.venv312/bin/pip install -r requirements.txt
```

## Start the app

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
./run_cds_app.sh
# or:
.venv312/bin/streamlit run app/demo_app.py
```

Browser opens at `http://localhost:8501`.

## Tabs

| Tab | Purpose |
|-----|---------|
| **Example admission** | Pick a MIMIC cohort row; calibrated risk + local explanation |
| **Manual entry** | Simplified form (age, labs, demographics) |
| **Global SHAP (test set summary)** | Frozen mean \|SHAP\| from notebook §15B — does not change per admission |

## Thesis / defence line

> Prototype clinical decision-support interface: displays **calibrated CKD-related admission risk** and **explainability** from the locked MIMIC model (`logreg_sigmoid_cal`).

## Screenshot for report

Frozen thesis captures (already generated):

- `paper_assets/figures/fig_ui_*.png` (copies) — default demo: index **148**, `hadm_id=24251211`
- `outputs/supervisor_runs/fig_ui_*.png` (same files; notebook write path)

**Polish features:** hero header, clinical disclaimer, `hadm_id` search, patient summary row, About / Developer expanders in sidebar.
