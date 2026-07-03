# Chapter 4 — Implementation and Results (draft for thesis)

Paste into your DIU report; adjust figure/table numbering to match your List of Tables/Figures.

---

## 4.1 Environment Setup

### 4.1.1 Hardware and Software

Experiments were conducted in Python **3.12** using a project virtual environment (`.venv312`). Core libraries included **pandas**, **NumPy**, **scikit-learn**, **PyTorch** (tabular MLP/ResMLP), **XGBoost**, **SHAP**, and **Streamlit** (CDS prototype). The supervisor pipeline notebook is `ckd_supervisor_pipeline_from_scratch.ipynb`; reusable modules live under `src/`.

### 4.1.2 Data Locations

| Source | Path (resolved at runtime) |
|--------|----------------------------|
| MIMIC-IV v3.1 `hosp` | `STUDY/Dataset/mimic-iv-3.1/hosp/` |
| NHANES curated CSV | `STUDY/Dataset/nhanes_ckd/csv/` |
| WESAD | `STUDY/Dataset/WESAD/` |

Artifacts are written to `CKD Dataset/outputs/supervisor_runs/`.

### 4.1.3 Splitting Policy

Train/validation/test partitions were created **programmatically** (not folder-based class splits). MIMIC admissions were grouped by `subject_id` (60% / 20% / 20%). NHANES used a held-out test split on the modeling table. WESAD windows were grouped by subject for holdout evaluation.

---

## 4.2 NHANES Clinical Branch (Notebook §1–§10)

### 4.2.1 Cohort and Label

NHANES cycle **2013–2014** was merged (DEMO + BIOPRO) with **4,702** modeling rows after leakage-safe feature drops. The binary label was **eGFR < 60 mL/min/1.73 m²** from serum creatinine (CKD-EPI 2021), prevalence **~6.6%**.

### 4.2.2 Preprocessing and Models

Median imputation and standard scaling were fit on the training split only. Models compared: logistic regression, tabular MLP, **ResMLP**, random forest, and XGBoost.

### 4.2.3 Results

**Table 4.1: NHANES test-set performance (separate cohort — not merged with MIMIC).**

| Model | Accuracy | F1 | Recall | Specificity | AUROC | AUPRC | ECE |
|-------|----------|-----|--------|-------------|-------|-------|-----|
| XGBoost | 0.966 | 0.798 | 0.913 | 0.970 | **0.992** | 0.932 | 0.014 |
| Baseline LogReg | 0.939 | 0.692 | 0.928 | 0.940 | 0.982 | 0.852 | 0.053 |
| Random Forest | 0.948 | 0.714 | 0.884 | 0.953 | 0.979 | 0.832 | 0.027 |
| Tabular MLP | 0.946 | 0.687 | 0.812 | 0.956 | 0.978 | 0.826 | 0.022 |
| ResMLP | 0.962 | 0.723 | 0.681 | 0.984 | 0.971 | 0.816 | 0.032 |

**Interpretation:** NHANES shows strong discrimination on population survey/laboratory features. This branch establishes the **clinical tower** on a public epidemiological cohort. It is **not** the primary hospital admission evidence and **must not** be averaged with MIMIC metrics.

*Artifact:* `from_scratch_clinical_nhanes_summary.csv`

---

## 4.3 MIMIC Admission Branch — Primary Evidence (Notebook §12+)

### 4.3.1 Cohort and Features

**30,000** index admissions were sampled from MIMIC-IV `hosp` tables. CKD proxy positive rate **15.2%** (ICD-9 585*, ICD-10 N18*). **68** tabular features: demographics, admission metadata, and laboratory medians within **48 hours** of admission (creatinine, BUN, electrolytes, hemoglobin, platelet, etc.).

### 4.3.2 Model Comparison (Uncalibrated Test Set)

**Table 4.2: MIMIC admission branch — held-out test performance.**

| Model | Accuracy | F1 | AUROC | AUPRC | ECE |
|-------|----------|-----|-------|-------|-----|
| XGBoost | 0.649 | 0.409 | **0.768** | 0.382 | 0.207 |
| Random Forest | 0.684 | 0.423 | 0.768 | 0.367 | 0.198 |
| Tabular MLP | 0.645 | 0.406 | 0.766 | 0.386 | 0.028 |
| Logistic Regression | 0.702 | 0.417 | 0.761 | 0.380 | 0.249 |

Discrimination is **moderate and similar across families** (AUROC ~0.76–0.77). Uncalibrated logistic regression shows **poor calibration** (ECE ≈ 0.25).

*Artifact:* `step2_mimic_admission_summary_extended.csv`

### 4.3.3 Calibration (Primary Reporting Model)

Post-hoc **sigmoid (Platt)** and **isotonic** calibration were fit on the validation split. The locked primary model is **`logreg_sigmoid_cal`**.

**Table 4.3: Calibration comparison on MIMIC test set.**

| Model | Threshold | F1 | Recall | Specificity | AUROC | ECE | Brier |
|-------|-----------|-----|--------|-------------|-------|-----|-------|
| LogReg uncalibrated | 0.52 | 0.417 | 0.658 | 0.711 | 0.761 | 0.249 | 0.195 |
| **LogReg sigmoid cal** | **0.16** | **0.415** | **0.674** | **0.696** | **0.761** | **0.020** | **0.119** |
| LogReg isotonic cal | 0.12 | 0.404 | 0.775 | 0.602 | 0.761 | 0.014 | 0.119 |

Sigmoid calibration reduced ECE by an order of magnitude with **unchanged AUROC**, supporting use of predicted probabilities in a decision-support setting.

*Artifact:* `step2_mimic_calibration_summary.csv`, `final_reporting_lock.json`

### 4.3.4 Confusion Matrix (Primary Model)

At F1-optimal threshold **0.16** on the test set (**n = 5,997**):

| | Predicted negative | Predicted positive |
|--|-------------------|-------------------|
| **Actual negative** | TN = 3,560 | FP = 1,468 |
| **Actual positive** | FN = 330 | TP = 639 |

*Figure 4.4:* `fig_mimic_confusion_matrix_logreg_sigmoid_cal.png`

### 4.3.5 Split Robustness (Five Seeds)

Grouped re-sampling by `subject_id` (seeds 42–46) for logistic regression:

| Metric | Mean ± SD |
|--------|-----------|
| AUROC | **0.769 ± 0.007** |
| F1 | 0.401 ± 0.015 |
| Recall | 0.742 ± 0.061 |
| Specificity | 0.649 ± 0.061 |
| ECE (uncalibrated sweep) | 0.261 ± 0.008 |

Low AUROC variance indicates **stable ranking** across partitions; recall variance highlights sensitivity to split choice for screening policies.

*Artifact:* `step2_mimic_robustness_mean_std.csv`

### 4.3.6 Temporal External Validation (MIMIC)

Train on earlier admissions; test on later admissions (80% temporal cutoff, subject-first index admission):

| Split | Test AUROC | ECE | F1 | Recall | Specificity |
|-------|------------|-----|-----|--------|-------------|
| Temporal external | **0.771** | 0.022 | 0.442 | 0.715 | 0.680 |
| Grouped test (reference) | 0.761 | — | — | — | — |

Temporal AUROC was **within ~0.01** of the grouped test AUROC, supporting internal external validity within MIMIC.

*Artifact:* `step2_mimic_temporal_external_summary.csv`

### 4.3.7 Explainability (SHAP)

Global SHAP on the primary logistic model ranked **anchor_age**, **insurance (Medicare)**, **race**, **admission type**, and **length of stay** among the strongest attributions; **lab_urea_nitrogen (BUN)** was the leading laboratory feature.

*Figure 4.3:* `fig_mimic_shap_top10.png`  
*Artifact:* `step2_mimic_shap_top15.csv`

### 4.3.8 Figures Summary (MIMIC)

| Figure | File | Description |
|--------|------|-------------|
| 4.1 | `fig_mimic_calibration_reliability.png` | Reliability diagram: uncalibrated vs sigmoid-calibrated LogReg |
| 4.2 | `fig_mimic_model_auroc.png` | Bar chart of test AUROC across model families |
| 4.3 | `fig_mimic_shap_top10.png` | Top-10 mean \|SHAP\| features |
| 4.4 | `fig_mimic_confusion_matrix_logreg_sigmoid_cal.png` | Confusion matrix at threshold 0.16 |

---

## 4.4 Wearable Branch — WESAD (Notebook §16)

### 4.4.1 Task and Data

**15 subjects**, **578 windows** from wrist signals (BVP, EDA, temperature, accelerometer magnitude). Label: **stress vs baseline** (not CKD).

### 4.4.2 Results

| Metric | Value |
|--------|-------|
| AUROC | 0.764 |
| AUPRC | 0.775 |
| F1 | 0.667 |
| Accuracy | 0.812 |

**Role in thesis:** Demonstrates the **wearable encoding tower** and export of branch probabilities for fusion protocol documentation. **Not** CKD detection.

*Artifact:* `wearable_branch_summary.json`

---

## 4.5 Multimodal Fusion Protocol (Notebook §14)

Late fusion combines **branch-level probabilities** with weights derived from branch AUROC+AUPRC (`step3_fusion_protocol.json`). Cells §14D–14E include a **branch-level proxy demonstration** because NHANES, MIMIC, and WESAD share **no patient IDs**.

**Table 4.4: Fusion meta-learner comparison (proxy holdout — illustrative only).**

| Method | AUROC | F1 | ECE |
|--------|-------|-----|-----|
| Static weighted | 0.497 | 0.254 | 0.748 |
| Meta-logreg on branch probs | 0.519 | 0.258 | 0.357 |

These values **do not** support a claim that multimodal fusion improves CKD prediction. Fusion is reported as **architecture and protocol**, with honest scope in Section 6.2.

*Artifacts:* `fusion_meta_comparison.csv`, `fusion_final_evaluation_status.json`

---

## 4.6 Clinical Decision-Support Prototype

A Streamlit application (`demo_app.py`) loads frozen MIMIC checkpoint artifacts and displays:

- Calibrated CKD-related admission risk (%)
- Adjustable decision threshold (default 0.16)
- Local logistic contributions and global SHAP tab

**Run:** see `UI_RUN.md`. Capture screenshots for this section after **`do 5`**.

---

## 4.7 Discussion

### 4.7.1 Principal Findings

1. **MIMIC** provides the defensible clinical core: moderate AUROC (~0.76), **strong calibration after Platt scaling** (ECE ~0.02), grouped and temporal validation, and SHAP interpretability.
2. **NHANES** shows high discrimination on a **different label and feature space** (population eGFR proxy).
3. **WESAD** validates wearable signal processing on a **proxy physiology task**.
4. **Fusion** is specified but **not empirically validated** on aligned CKD patients.

### 4.7.2 Comparison to Project Objectives

| Objective | Status |
|-----------|--------|
| Multimodal framework | Achieved (three towers + fusion protocol) |
| Early CKD-related risk on EHR | Achieved on MIMIC (proxy label) |
| Wearable integration | Demonstrated (WESAD); not CKD-linked |
| Explainable AI | Achieved (SHAP, permutation, UI explanations) |
| Medical imaging | Not implemented |

### 4.7.3 Limitations

See **Chapter 6, Section 6.2** (`THESIS_6_2_LIMITATIONS.md`).

---

## 4.8 Summary

Chapter 4 presented implementation and results for three disjoint public cohorts. **MIMIC admission-level modeling** is the primary evaluated contribution; NHANES and WESAD support separate clinical and wearable branches; fusion remains a **documented protocol** pending aligned multimodal data.
