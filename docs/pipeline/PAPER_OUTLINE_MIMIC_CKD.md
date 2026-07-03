# Journal paper outline (MIMIC-only)

**Purpose:** Publishable spin-off from the thesis — **not** the full multimodal + WESAD + fusion story.

**Working title:**  
*Calibrated and explainable admission-level chronic kidney disease risk prediction on MIMIC-IV*

**Alternative shorter title:**  
*Platt-calibrated logistic models for early CKD risk at hospital admission: a MIMIC-IV study*

---

## What to include vs cut from thesis

| Include | Cut or move to supplementary / future work |
|---------|---------------------------------------------|
| MIMIC cohort, labels, features | NHANES as main result |
| Grouped splits by `subject_id` | WESAD wearable branch |
| LogReg + calibration (sigmoid/isotonic) | Cross-dataset fusion (14D proxy) |
| Baselines: MLP, RF, XGB (same split) | “99% accuracy” NHANES claims |
| Operating points (F1, target-recall) | CDS deployed UI |
| 5-seed robustness + bootstrap CI | Meta-fusion on proxy holdout |
| Permutation + SHAP (EHR) | Grad-CAM on WESAD |
| Calibration reliability figure | Full title “wearable detects CKD” |

---

## Target venues (realistic path)

| Tier | Examples | When |
|------|----------|------|
| Workshop / conference | ML4H, IEEE EMBC, HEALTHINF | First submission after thesis |
| Applied Q2–Q3 | *Journal of Biomedical Informatics* (ambitious), *Computer Methods and Programs in Biomedicine*, *BMC Medical Informatics* | After 1–2 reviewer rounds of extra analysis |
| Q1 | *Lancet Digital Health*, *NPJ Digital Medicine*, *JAMIA* top tier | Only after temporal validation + novelty + possibly clinician co-author |

**Do not submit** the full thesis narrative to Q1 as one paper.

---

## Abstract template (~250 words)

**Background:** Chronic kidney disease (CKD) is often recognized late. Admission-level electronic health records may support early risk stratification if models are leakage-aware, calibrated, and interpretable.

**Objective:** To develop and evaluate calibrated machine learning models for CKD-related admission risk using MIMIC-IV tabular data.

**Methods:** We constructed an admission-level cohort (n=30,000 admissions) with CKD proxy labels from ICD-9/10 (585*, N18*). Features included demographics, admission metadata, and admission-window laboratory aggregates. We used subject-level grouped train/validation/test splits, compared logistic regression, multilayer perceptron, random forest, and XGBoost, applied post-hoc sigmoid and isotonic calibration, and evaluated discrimination (AUROC, AUPRC), calibration (ECE, Brier), and operating points (F1-optimal and high-recall screening). Robustness was assessed over five split seeds with bootstrap confidence intervals. Explainability used permutation importance and SHAP on the primary calibrated logistic model.

**Results:** Test-set AUROC for the primary calibrated logistic model was 0.761 (ECE 0.020 vs 0.249 uncalibrated). Tree and neural baselines achieved similar discrimination (AUROC ~0.766–0.768). Repeated grouped validation yielded mean AUROC 0.769 ± 0.007. Top attributions included age, insurance, admission type, and laboratory features.

**Conclusions:** Calibrated tabular models provide moderate but stable CKD-related admission risk discrimination on MIMIC-IV. Probability calibration materially improves reliability for clinical-facing interpretation. External temporal validation and multimodal extensions are needed before deployment.

**Keywords:** chronic kidney disease; MIMIC-IV; calibration; explainable AI; risk prediction; electronic health records

---

## 1. Introduction (~1.5 pages)

### 1.1 Clinical motivation
- CKD prevalence, late diagnosis, potential value of admission risk flags.
- Difference between **diagnosis** and **risk stratification** (decision support, not treatment).

### 1.2 Related work (must cite — fill from literature search)
- MIMIC sepsis/AKI/CKD prediction papers.
- Calibration in clinical ML (Guo et al., Platt scaling).
- Explainability in EHR (SHAP in healthcare).
- Gap: many papers report AUROC only; fewer report **grouped splits + calibration + threshold policies** together on CKD admission proxies.

### 1.3 Contributions (bullet list — keep narrow)
1. Leakage-aware admission-level CKD proxy cohort on MIMIC-IV with lab time windows.
2. Systematic comparison of classical, tree, and neural tabular models on **identical splits**.
3. Post-hoc calibration with quantified ECE/Brier improvement.
4. Operating-point analysis for balanced vs screening-oriented thresholds.
5. Split stability over five seeds and global explainability analysis.

### 1.4 What this paper does **not** claim
- Wearable CKD detection; multimodal fusion; prospective deployment.

---

## 2. Materials and methods (~3–4 pages)

### 2.1 Data source
- MIMIC-IV v3.1 `hosp` module; PhysioNet credentialing statement.
- Admission sampling (30,000), positive rate ~15.2%.

### 2.2 Outcome definition
- ICD-9 `585*`, ICD-10 `N18*` at admission level.
- Limitation: proxy label vs formal eGFR staging (state explicitly).

### 2.3 Features
- Demographics, admission fields, lab aggregates (`lab_*`).
- Admission time window for labs (48h in final run).
- Leakage exclusions (list from notebook).

### 2.4 Preprocessing
- Train-only imputation and scaling.
- No test statistics leakage.

### 2.5 Splits
- Grouped by `subject_id`: train / val / test.
- Assertion: no group overlap.
- Optional **add before submission:** temporal split (train early years, test later).

### 2.6 Models
- Logistic regression (class-weight balanced).
- Tabular MLP.
- Random forest, XGBoost (`12F` settings — document hyperparameters).

### 2.7 Calibration
- Sigmoid (Platt) and isotonic on validation set.
- Primary: `logreg_sigmoid_cal`.

### 2.8 Threshold selection
- F1-optimal on validation (primary).
- Target recall ≥ 0.85 (screening scenario).
- Youden (optional supplementary).

### 2.9 Metrics
- AUROC, AUPRC, accuracy, F1, recall, specificity, ECE, Brier.
- 5 seeds: mean ± std; bootstrap 95% CI for AUROC/F1.

### 2.10 Explainability
- Permutation importance (held-out sample).
- SHAP LinearExplainer on logistic backbone.
- Case examples (high-risk TP, low-risk TN) — qualitative only.

### 2.11 Software & reproducibility
- Python, scikit-learn, PyTorch (MLP), SHAP.
- Point to public code/artifacts policy (what you can release).

---

## 3. Results (~2–3 pages)

### Table 1 — Cohort characteristics
- N admissions, N subjects, prevalence, feature count, lab availability.

### Table 2 — Test-set model comparison (from `step2_mimic_admission_summary_extended.csv`)
| Model | AUROC | AUPRC | F1 | ECE |
| LogReg raw | 0.761 | 0.380 | 0.417 | 0.249 |
| LogReg sigmoid cal | **0.761** | 0.379 | 0.415 | **0.020** |
| MLP | 0.766 | 0.386 | 0.406 | 0.028 |
| RF | 0.768 | 0.367 | 0.423 | 0.198 |
| XGB | 0.768 | 0.382 | 0.409 | 0.207 |

### Table 3 — Operating points (`step2_mimic_operating_point_summary.csv`)
- F1 vs target-recall policies for primary model.

### Table 4 — Robustness (`step2_mimic_robustness_mean_std.csv`)
- AUROC 0.769 ± 0.007 (5 seeds).

### Figure 1 — Study flow (CONSORT-style diagram)
- Cohort selection → split → models → calibration.

### Figure 2 — Calibration reliability (`fig_mimic_calibration_reliability.png`)
- Uncalibrated vs sigmoid.

### Figure 3 — Model AUROC comparison (`fig_mimic_model_auroc.png`)

### Figure 4 — SHAP top features (`fig_mimic_shap_top10.png`)

### Optional Figure 5 — Subgroup AUROC (add before submission)
- Age / sex strata.

---

## 4. Discussion (~1.5 pages)

### 4.1 Summary of findings
- Moderate discrimination; calibration essential; baselines competitive.

### 4.2 Clinical interpretation
- Screening vs balanced tradeoffs (recall ~67% at F1 point vs higher recall scenario).
- Not a replacement for creatinine/eGFR testing.

### 4.3 Comparison to literature
- Place AUROC ~0.76 in context of other MIMIC tabular tasks.

### 4.4 Limitations
- Single database; proxy ICD labels; tabular only; no prospective validation; fairness not fully explored; sklearn version pickle warning if applicable.

### 4.5 Future work
- Temporal validation; vitals + notes same cohort; fairness; prospective pilot.

---

## 5. Conclusion (~0.5 page)
- One paragraph: calibrated tabular admission models + explainability + robustness protocol; deployment requires external validation.

---

## Supplementary material
- Full hyperparameters.
- Per-seed metrics (`step2_mimic_robustness_per_seed.csv`).
- Case table (`step2_mimic_case_examples.csv`).
- NHANES mention: optional one paragraph “generalizability exploratory only.”

---

## Pre-submission checklist (add before sending)

- [ ] Literature review: 15–25 recent MIMIC / CKD / calibration papers cited.
- [ ] Temporal split experiment OR justify why not.
- [ ] Subgroup fairness table (age, sex, race).
- [ ] Related-work comparison table (at least 2–3 prior MIMIC papers).
- [ ] IRB / data use statement for MIMIC.
- [ ] Code availability statement.
- [ ] Remove all WESAD/fusion from main text.
- [ ] Professional English edit.
- [ ] Co-author: supervisor review.

---

## Timeline after thesis defence

| Week | Task |
|------|------|
| 1–2 | Draft Introduction + Methods from thesis Ch.3 |
| 3 | Results tables + figures (already exist) |
| 4 | Discussion + related work search |
| 5 | Supervisor revision |
| 6 | Submit to workshop or Q2–Q3 journal |

---

## One-sentence pitch to supervisor

> “The publishable unit is the **MIMIC calibrated risk paper**; the thesis remains the **broader multimodal framework** with wearable and fusion as architectural future work.”

---

*Generated from artifacts in `outputs/supervisor_runs/` — align numbers if you re-run 12B.*
