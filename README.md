# Deep Learning Framework for Early CKD Detection

This repository contains a reproducible research workflow for **early detection of chronic kidney disease (CKD)** across four modality branches:

- Population clinical (NHANES)
- Hospital EHR — primary (MIMIC-IV)
- Wearable physiology — proxy (WESAD)
- Multimodal fusion — protocol stub (not same-patient aligned)

The project compares population clinical modeling, hospital EHR risk prediction, wearable physiology proxies, and exploratory multimodal fusion for renal-related risk estimation with explainable AI.

> **Note:** This repository is intended for research and educational use. It is not a clinical diagnostic tool.

---

## Project Overview

The study evaluates multiple CKD-related risk modeling strategies on NHANES, MIMIC-IV, and WESAD using logistic regression, calibrated logistic regression, tabular MLPs, tree baselines, wearable window features, and exploratory fusion. The workflow includes dataset verification, cohort-specific label definitions, grouped train/validation/test splits, leakage checks, model training, calibration, operating-point selection, test evaluation, robustness checks, explainability, qualitative visualizations, bootstrap-style repeated splits, and a clinical decision-support demo.

### Main model families

| Family | Models |
|---|---|
| NHANES population clinical | Logistic regression, Tabular MLP, Residual MLP, Random Forest, XGBoost |
| MIMIC admission EHR (primary) | Logistic regression, logreg_sigmoid_cal, isotonic calibration, Tabular MLP, ResMLP, RF, XGBoost |
| Wearable proxy (WESAD) | Wearable RF on BVP/EDA/ACC window statistics |
| Multimodal fusion (exploratory) | Static weighted fusion, meta-logreg on branch probabilities |

---

## Completed Workflow

The final project workflow contains the following sections:

1. Environment setup
2. Dataset verification
3. NHANES clinical label definition
4. NHANES feature engineering
5. NHANES grouped train/val/test split
6. NHANES data leakage checks
7. NHANES baseline and deep models
8. NHANES tree baselines
9. NHANES reproducible artifact export
10. MIMIC admission-level cohort construction
11. MIMIC grouped split and preprocessing
12. MIMIC baseline, MLP, ResMLP, and tree baselines
13. MIMIC operating-point comparison
14. MIMIC repeated-split robustness
15. MIMIC probability calibration
16. Final reporting lock
17. MIMIC temporal external validation
18. MIMIC SHAP explainability
19. Multimodal fusion protocol (NHANES + MIMIC)
20. Wearable branch demo (WESAD)
21. Fusion stub and meta-learner comparison
22. Final global comparison
23. Admission-level metrics
24. Calibration and AUROC visualizations
25. Ablation-style model comparison
26. Final visualizations
27. Paper-ready discussion
28. Limitations
29. Conclusion
30. Reproducibility checklist
31. Clinical decision-support demo app
32. Progress report artifact pack

Canonical notebook: `notebooks/ckd_supervisor_pipeline_from_scratch.ipynb` — run cells under **SUPERVISOR RUN ORDER**, one at a time.

---

## Key Results

### Primary evaluation (MIMIC admission-level, test set)

The locked primary model was:

| Model | Test AUROC | Test F1 | ECE | Recall | Specificity |
|---|---:|---:|---:|---:|---:|
| logreg_sigmoid_cal | 0.7614 | 0.4145 | 0.0203 | 0.6739 | 0.6959 |

Locked operating threshold: **0.16** · ~30,000 admissions · 68 features · positive rate ~15.2%

Comparison on the same MIMIC test split:

| Model | Test AUROC | Test F1 | ECE |
|---|---:|---:|---:|
| logreg_sigmoid_cal | 0.7614 | 0.4145 | 0.0203 |
| logreg_uncalibrated | 0.7614 | 0.4167 | 0.2486 |
| Tabular MLP | 0.7769 | 0.3997 | 0.0160 |

### Secondary evaluation (NHANES population clinical, separate cohort)

| Model | Test AUROC | Test F1 | Balanced accuracy |
|---|---:|---:|---:|
| Logistic regression | 0.9822 | 0.6919 | 0.9339 |

### Wearable proxy evaluation (WESAD)

| Task | Model | Holdout AUROC |
|---|---|---:|
| Stress vs baseline | Wearable RF | 0.7639 |

### Main findings

- logreg_sigmoid_cal achieved the best balance of calibration and interpretability on the primary MIMIC cohort.
- Sigmoid calibration improved ECE without changing ranking AUROC; the operating threshold moved to 0.16.
- Tabular MLP was numerically competitive on AUROC but was not selected as the locked primary model.
- NHANES logistic regression achieved very high AUROC on its own cohort, but that cohort is not directly comparable to MIMIC admissions.
- WESAD supports wearable feature feasibility only; it cannot support CKD detection claims.
- Multimodal fusion remains a protocol and proxy evaluation because NHANES, MIMIC, and WESAD are not linked by patient ID.
- Centralized MIMIC supervised learning remained stronger than the exploratory fusion stub in the current setup.
- External validation is needed before making clinical generalization claims.

---

## Repository Structure

Recommended structure:

```text
CKD Dataset/
├── README.md
├── requirements.txt
├── .gitignore
├── run_cds_app.sh
├── notebooks/
│   └── ckd_supervisor_pipeline_from_scratch.ipynb
├── src/
│   ├── data/
│   ├── models/
│   ├── eval/
│   ├── config/
│   └── utils/
├── app/
│   └── demo_app.py
├── configs/
├── scripts/
├── data/
│   ├── README.md
│   ├── DATASET_INVENTORY.md
│   └── datasets/
├── paper_assets/
│   ├── figures/
│   ├── tables/
│   └── diagrams/
└── artifacts/
    └── README.md
```

Large trained checkpoints, raw MIMIC/NHANES/WESAD data, and generated artifacts should generally **not** be committed directly to GitHub. Use a submission zip, cloud storage, or an external artifact registry for large files. Frozen runs are stored under `outputs/supervisor_runs/` (see `artifacts/README.md`).

---

## Installation

Create and activate a Python environment:

```bash
cd "CKD Dataset"
python3.12 -m venv .venv312
```

Windows PowerShell:

```bash
.\.venv312\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv312/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Dataset

The project expects independent NHANES, MIMIC-IV, and WESAD sources with subject- or case-level identifiers inside each source, but not across sources.

Expected external layout:

```text
STUDY/Dataset/
├── mimic-iv-3.1/hosp/
├── nhanes_ckd/csv/
└── WESAD/
```

Recommended project-side layout:

```text
data/
├── README.md
├── DATASET_INVENTORY.md
└── datasets/   → symlink to STUDY/Dataset
```

Expected label conventions:

| Branch | Positive definition |
|---|---|
| NHANES | Clinical CKD rule from eGFR / ACR with leakage-safe feature handling |
| MIMIC | Admission-level CKD-related composite from labs and diagnoses |
| WESAD | Stress (2) vs baseline (1), not CKD |

Raw data is excluded from Git by default.

Regenerate inventory:

```bash
python3 scripts/scan_datasets.py
```

Peek loaders:

```bash
.venv312/bin/python scripts/load_ckd_datasets.py --peek
.venv312/bin/python scripts/load_ckd_datasets.py --nhanes-cycle 2013-2014 --nrows 500
.venv312/bin/python scripts/load_ckd_datasets.py --mimic-module hosp --mimic-table admissions --nrows 200
.venv312/bin/python scripts/load_ckd_datasets.py --wesad S10
```

---

## Training and Evaluation

The notebook workflow trains and evaluates:

- Logistic regression and calibrated variants
- Tabular MLP and Residual MLP
- Random Forest and XGBoost baselines
- Wearable RF on WESAD window features
- Exploratory fusion and meta-learner comparison

Evaluation includes:

- Global admission-level metrics
- Per-model AUROC, AUPRC, F1, precision, recall, specificity, balanced accuracy
- Expected calibration error and Brier score
- Grouped split leakage checks
- Repeated-split robustness
- Temporal external validation
- SHAP global and local explanations
- Qualitative visualization and case review
- Branch-level fusion proxy comparison

---

## Inference

The project includes a clinical decision-support prototype for selected MIMIC admissions and simplified manual entry.

Outputs include:

- Original admission context
- Calibrated CKD-related risk score
- Thresholded alert status
- Local explanation summary
- Optional global SHAP summary tab

Important wording:

- Without ground-truth labels at inference time, outputs are **risk scores and confidence summaries**, not true diagnostic accuracy.
- With held-out labeled admissions during evaluation, AUROC, F1, precision, recall, specificity, balanced accuracy, ECE, and Brier score can be computed.

Start the app:

```bash
./run_cds_app.sh
```

---

## Paper Assets

Recommended paper-ready assets:

- Multimodal workflow diagram
- Dataset split and leakage-check summary
- Model family comparison figure
- MIMIC AUROC comparison figure
- Calibration reliability figure
- SHAP top-feature figure
- Confusion matrix for locked primary model
- CDS demo screenshots
- Supplementary tables for calibration and SHAP

---

## Reproducibility

The project records:

- Python version
- PyTorch version
- scikit-learn version
- Working directory
- Artifact root
- Random seed
- Grouped split configuration
- Locked model and threshold
- Bootstrap / repeated-split configuration where applicable

Final environment example:

| Item | Value |
|---|---|
| Python | 3.12.x |
| PyTorch | ≥2.0 |
| scikit-learn | ≥1.3 |
| Platform | macOS |
| Primary model | logreg_sigmoid_cal |
| Primary threshold | 0.16 |
| Checkpoint | step2_mimic_checkpoint.pkl |

---

## Limitations

- Single-hospital primary evidence from MIMIC
- Tabular admission-level modeling rather than imaging-based diagnosis
- No same-patient multimodal alignment across NHANES, MIMIC, and WESAD
- WESAD has no CKD labels
- Sparse creatinine coverage in the MIMIC admission window
- Simulated fusion rather than prospective multimodal validation
- Limited hyperparameter search
- No expert qualitative clinical review
- No formal external state-of-the-art benchmark on identical splits
- External validation is required before making clinical generalization claims

---

## Citation

If this project is used in academic work, please cite the repository and related datasets/methods appropriately.

```bibtex
@misc{ckd_multimodal_xai_fydp,
  title  = {A Deep Learning Framework for Early Detection of Chronic Kidney Disease: Integrating Multi-Modal Data from Wearable Devices and Clinical Records with Explainable AI},
  author = {Tahsin, Md. Shadman},
  year   = {2026},
  note   = {Multi-modal tabular CKD risk modeling with calibration, SHAP, and exploratory fusion}
}
```

---

## License

Choose a license before public release. Recommended options:

- MIT License for open research code
- Apache-2.0 for permissive open-source release
- Private repository if dataset/checkpoint restrictions apply

---

## Disclaimer

This software is for research purposes only and is not intended for clinical diagnosis or treatment planning.
