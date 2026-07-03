# Chapter 3 — Methodology (draft for DIU thesis / pre-defense)

Paste into Word Chapter 3. Align figure numbers with your List of Figures.

---

## 3.1 Overview

The methodology follows a **branch-wise multimodal pipeline**: three independent data sources (NHANES, MIMIC-IV, WESAD) are preprocessed separately, models are trained per branch, the primary hospital model is calibrated and explained, and a **late-fusion protocol** combines branch-level probabilities where alignment permits only proxy evaluation.

Implementation is centralized in `notebooks/ckd_supervisor_pipeline_from_scratch.ipynb` with reusable modules under `src/`.

**Design principle:** no patient-level merge across NHANES, MIMIC, and WESAD; fusion operates on **probability outputs**, not a unified multimodal table.

---

## 3.2 Data Sources

| Branch | Dataset | Unit of analysis | Label |
|--------|---------|------------------|-------|
| Population clinical | NHANES 2013–2014 (DEMO + BIOPRO) | Participant row | eGFR &lt; 60 (CKD-EPI from creatinine) |
| Hospital EHR (primary) | MIMIC-IV v3.1 `hosp` | Admission (`hadm_id`) | ICD CKD proxy (585* / N18*) |
| Wearable proxy | WESAD | Signal window | Stress vs baseline (not CKD) |

Data paths resolve at runtime to `STUDY/Dataset/` via `resolve_*()` helpers in the supervisor notebook.

---

## 3.3 Preprocessing and Feature Engineering

### 3.3.1 NHANES

1. Merge cycle CSV tables on `SEQN`.
2. Construct binary CKD label from eGFR rule; drop label-defining leakage columns (`LBXSCR`, `RIDAGEYR`, etc.).
3. Median imputation and standard scaling **fit on train only**.
4. Random or held-out split on modeling table (~4,702 rows after cleaning).

### 3.3.2 MIMIC-IV

1. Sample **30,000** index admissions from `hosp` tables.
2. Join demographics, admission metadata, and **laboratory medians within 48 hours** of admission (creatinine, BUN, electrolytes, hemoglobin, platelet).
3. Construct **68** tabular features; CKD proxy from diagnosis codes.
4. **Grouped split by `subject_id`** (60% / 20% / 20%) to prevent leakage across admissions from the same patient.

### 3.3.3 WESAD

1. Load wrist pickle per subject (`BVP`, `EDA`, `TEMP`, `ACC`).
2. Window signals: **1920 samples** (~30 s), stride **960**.
3. Extract per-window statistics (mean, std, min, max) per channel.
4. Label windows by majority protocol label (baseline=1, stress=2 → binary stress proxy).
5. Grouped holdout by **subject_id** for evaluation.

---

## 3.4 Models and Training

Five algorithm families were compared per branch where applicable:

| Algorithm | Type | Branches |
|-----------|------|----------|
| Logistic regression | ML | NHANES, MIMIC, WESAD, fusion meta |
| Random forest | ML | NHANES, MIMIC, WESAD |
| XGBoost | ML | NHANES, MIMIC |
| Tabular MLP | DL (PyTorch) | NHANES, MIMIC |
| Tabular ResMLP | DL (PyTorch) | NHANES |

**Primary locked model (MIMIC):** sigmoid-calibrated logistic regression (`logreg_sigmoid_cal`), threshold **0.16** from validation F1 policy.

Training conventions:
- Class imbalance: `class_weight='balanced'` where supported.
- Deep models: Adam, cross-entropy, early stopping on validation AUROC.
- Tree models: Youden threshold on validation, applied to test.

---

## 3.5 Calibration

Post-hoc calibration on MIMIC validation split:
- **Sigmoid (Platt)** — selected primary.
- **Isotonic** — comparator.

Metrics: **ECE**, Brier score, reliability diagrams. Uncalibrated logistic ECE ≈ 0.25 reduced to ≈ 0.02 after sigmoid calibration at unchanged AUROC (~0.76).

---

## 3.6 Explainability (XAI)

- **Global SHAP** on MIMIC held-out test set for locked logistic model.
- **Local explanations** in CDS prototype via logistic coefficient–based contributions and case review.
- Artifacts: `step2_mimic_shap_top15.csv`, `fig_mimic_shap_top10.png`.

---

## 3.7 Late Fusion Protocol

Because NHANES, MIMIC, and WESAD share **no patient identifiers**:

1. Train each branch independently; export **calibrated branch probabilities**.
2. Compute branch **quality weights** from normalized (AUROC + AUPRC) on validation summaries.
3. **Static weighted fusion:**  
   `p_fused = Σ w_b · p_b`
4. **Meta-logistic regression** on branch probability features (comparator).
5. **Proxy holdout demo** where aligned cohort unavailable — documented as protocol, not clinical validation.

Fusion specification: `outputs/supervisor_runs/step3_fusion_protocol.json`.

---

## 3.8 Evaluation Metrics

| Category | Metrics |
|----------|---------|
| Discrimination | AUROC, AUPRC |
| Classification | Accuracy, F1, sensitivity, specificity, balanced accuracy |
| Calibration | ECE, Brier score |
| Robustness | Multi-seed grouped re-split (MIMIC) |
| Temporal validity | Time-based holdout within MIMIC |

---

## 3.9 Clinical Decision-Support Prototype

Streamlit application (`app/demo_app.py`) loads frozen MIMIC checkpoint and presents:
- Example admission risk + local explanation
- Manual feature entry
- Global SHAP summary (fixed test-set)

**Disclaimer:** research demonstration only; not deployed clinically.

---

## 3.10 Reproducibility

- Python 3.12 (`.venv312`), pinned requirements in `requirements.txt`.
- Artifacts under `outputs/supervisor_runs/`; thesis copies in `paper_assets/`.
- Locked reporting: `final_reporting_lock.json`.
- Regenerate figures: `scripts/prepare_predefense.sh`.

---

## 3.11 Methodology Limitations (summary)

- No same-patient multimodal cohort.
- WESAD branch is physiology proxy, not CKD-labeled.
- Primary evidence is **tabular admission-level** MIMIC, not NLP discharge text or imaging.
- Fusion evaluation partially uses **proxy/synthetic holdout** where alignment is impossible.

Full discussion: Chapter 6.2 (`THESIS_6_2_LIMITATIONS.md`).
