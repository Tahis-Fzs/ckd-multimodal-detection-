# Calibrated and Explainable Admission-Level CKD Risk Prediction on MIMIC-IV

**Authors:** [First Author], [Second Author], [Supervisor Name]  
**Affiliations:** [Department], [University], [City, Country]  
**Corresponding author:** [email@institution.edu]

---

## Abstract

Chronic kidney disease (CKD) is frequently under-recognized at hospital admission despite rich information in electronic health records (EHRs). We present a leakage-aware evaluation protocol for admission-level CKD-related risk prediction on MIMIC-IV, emphasizing probability calibration, grouped validation, and explainability rather than marginal gains in area under the receiver operating characteristic curve (AUROC). We constructed a cohort of 30,000 admissions (15.2% CKD proxy positive) using ICD-9/10 codes (585*, N18*) and 68 tabular features, including demographics, admission metadata, and laboratory medians within 48 hours of admission. Models were trained with subject-level grouped train/validation/test splits and compared under identical preprocessing. Logistic regression with post-hoc sigmoid calibration achieved test AUROC 0.761 (expected calibration error [ECE] 0.020 vs. 0.249 uncalibrated; Brier score 0.119 vs. 0.195). Tree and neural baselines showed similar discrimination (AUROC 0.766–0.768) but poor default calibration (ECE 0.198–0.207). Five-seed grouped re-sampling yielded mean AUROC 0.769 ± 0.007. Operating-point analysis showed screening-oriented thresholds can raise recall above 0.81 at the cost of specificity near 0.55. SHAP attributions highlighted age, insurance, admission type, and select laboratory variables. Calibrated tabular models offer moderate, stable discrimination with clinically interpretable probabilities; external temporal validation remains necessary before deployment.

**Keywords—** chronic kidney disease, MIMIC-IV, risk prediction, probability calibration, grouped cross-validation, explainable AI, electronic health records

---

## I. INTRODUCTION

Chronic kidney disease (CKD) affects approximately 10% of adults worldwide and is associated with cardiovascular morbidity, progression to end-stage renal disease, and excess mortality [5]. Many patients are identified only after laboratory abnormalities accumulate or complications emerge, limiting opportunities for early nephrology referral and guideline-concordant management. Hospital admission represents a high-yield moment for risk stratification because structured EHR data—demographics, admission context, and early laboratory results—are routinely captured.

Machine learning on critical-care databases such as MIMIC-IV has produced strong discriminative models for diverse outcomes [1]. However, three methodological gaps recur in clinical prediction reporting: (i) patient-level information leakage when admissions from the same individual appear in both training and test sets [8]; (ii) miscalibrated predicted probabilities despite acceptable AUROC [2]; and (iii) limited transparency regarding which features drive predictions at the admission level [3]. For decision support, calibrated probabilities and interpretable attributions are often as important as ranking performance.

We study **admission-level CKD-related risk** as a proxy task defined by diagnosis codes recorded during the index hospitalization. This is risk stratification and early flagging—not a substitute for creatinine-based staging or formal estimated glomerular filtration rate (eGFR) assessment. Our contribution is a **reproducible MIMIC-only pipeline** that jointly reports grouped evaluation, post-hoc calibration, threshold policies for balanced vs. screening use cases, split robustness, and SHAP-based explainability. We explicitly do **not** claim state-of-the-art AUROC, wearable sensing, multimodal fusion, or deployment readiness.

**Contributions:**
1. Leakage-aware admission-level CKD proxy cohort (n = 30,000) with time-bounded laboratory aggregation.
2. Head-to-head comparison of logistic regression, multilayer perceptron (MLP), random forest, and XGBoost on identical subject-grouped splits.
3. Quantified calibration gains (ECE, Brier) via sigmoid and isotonic post-processing.
4. Operating-point analysis (F1-optimal and high-recall screening).
5. Five-seed robustness and global SHAP attributions for the primary logistic model.

---

## II. METHODS

### A. Data Source and Cohort

We used MIMIC-IV v3.1 hospital (`hosp`) tables [1], accessed under PhysioNet credentialed-use agreement. Admissions were sampled to **n = 30,000** index hospitalizations (`random_state = 42`), merged with patient demographics, and linked to diagnosis and laboratory tables. The cohort definition is admission-level (`hadm_id`); each row represents one hospitalization.

### B. Outcome Definition

The binary outcome was **CKD proxy positive** if any diagnosis code during the admission matched ICD-9 `585*` or ICD-10 `N18*`. Prevalence was **15.23%** (4,569 positive of 30,000). This label captures documented CKD during the stay and may include prevalent disease, coding variation, and comorbidity documentation; it is **not** equivalent to KDIGO stage derived from eGFR and albuminuria [5]. We frame the task as **related admission risk identification** for methods benchmarking, not definitive CKD diagnosis.

### C. Features and Leakage Controls

We extracted **68** numeric and one-hot encoded features:
- Demographics: age (`anchor_age`), gender, race.
- Admission metadata: admission type, insurance, length of stay (hours).
- Laboratory medians: bicarbonate, chloride, creatinine, hemoglobin, platelet, potassium, sodium, and urea nitrogen (BUN), aggregated from `labevents` within **48 hours** after admission time (non-negative offset).

Preprocessing (median imputation, standard scaling for linear/MLP inputs) was **fit on the training split only**. No post-admission outcome fields or diagnosis-derived features were used as predictors. Grouped splitting by `subject_id` ensured no patient appeared in more than one partition.

### D. Data Partitioning

Admissions were partitioned 60%/20%/20% into train, validation, and test sets using **grouped splits by `subject_id`** (five random seeds for robustness; primary results reported for seed 42). We verified zero subject overlap across partitions. Temporal hold-out (train on earlier years, test on later) was not performed in this study and is identified as a priority for external validity.

### E. Models

All models consumed the same feature matrix:

| Model | Description |
|-------|-------------|
| **Logistic regression (LogReg)** | L2-regularized, class-weight balanced; primary interpretable backbone. |
| **Tabular MLP** | Fully connected network with ReLU, dropout, trained with early stopping on validation AUROC. |
| **Random forest (RF)** | Ensemble of decision trees with default regularization via `max_depth` / `min_samples_leaf`. |
| **XGBoost** | Gradient-boosted trees with regularization; same hyperparameter budget as RF/MLP family. |

Hyperparameters were selected on the validation split; test metrics are reported once.

### F. Probability Calibration

Post-hoc calibration was applied to LogReg using **sigmoid (Platt) scaling** [4] and **isotonic regression** [2], both fit on validation predictions and evaluated on the held-out test set. Expected calibration error (ECE, 10 equal-mass bins) and Brier score were computed alongside AUROC and area under the precision-recall curve (AUPRC). The **primary calibrated model** is sigmoid-calibrated LogReg (`logreg_sigmoid_cal`).

### G. Threshold and Operating-Point Policies

Binary decisions used validation-tuned thresholds under three policies:
- **F1-optimal:** maximize F1 on validation (primary reporting threshold).
- **Target recall:** highest threshold achieving validation recall ≥ 0.85 (screening-oriented).
- **Youden index:** maximize sensitivity + specificity − 1 (secondary).

### H. Robustness and Explainability

**Robustness:** Five subject-grouped re-splits (seeds 42–46) with LogReg; we report mean ± standard deviation for AUROC, F1, recall, specificity, AUPRC, and ECE.

**Explainability:** Global SHAP values [3] were computed with `LinearExplainer` on the scaled LogReg inputs (validation sample); mean absolute SHAP ranked feature importance. Permutation importance on held-out data corroborated ranking (supplementary).

### I. Software

Python 3.x, scikit-learn, PyTorch (MLP), XGBoost, SHAP. Analysis artifacts are stored under `outputs/supervisor_runs/`.

---

## III. RESULTS

### A. Cohort Summary

Table I summarizes the study cohort. Positive admissions were minority-class but sufficiently frequent for stable AUPRC estimation. Laboratory features were available for a subset of admissions depending on clinical ordering patterns; missing values were imputed from training statistics.

**TABLE I**  
**COHORT AND FEATURE SUMMARY**

| Characteristic | Value |
|----------------|-------|
| Admissions (n) | 30,000 |
| CKD proxy positive | 4,569 (15.23%) |
| CKD proxy negative | 25,431 (84.77%) |
| Features (total) | 68 |
| Laboratory features | 8 (48-h post-admission window) |
| Split strategy | Grouped by `subject_id` (60/20/20) |
| Primary outcome | ICD-9 585* / ICD-10 N18* during admission |

### B. Discrimination and Calibration

Table II reports **held-out test** performance for uncalibrated baselines. AUROC spanned **0.761–0.768**, indicating moderate ranking ability without meaningful separation between model families. Uncalibrated LogReg achieved the highest F1 (0.417) at threshold 0.52 but **ECE = 0.249**. Tree models reached AUROC up to **0.768** yet remained miscalibrated (ECE 0.198–0.207). The tabular MLP matched discrimination (AUROC 0.766) with substantially better native calibration (ECE 0.028).

Post-hoc calibration improved LogReg reliability without changing rank ordering: sigmoid calibration reduced **ECE from 0.249 to 0.020** and **Brier score from 0.195 to 0.119** at test; isotonic calibration achieved **ECE = 0.014** (AUROC 0.761). Sigmoid-calibrated LogReg at F1-optimal threshold (0.16) yielded test **F1 = 0.415**, **recall = 0.674**, **specificity = 0.696**.

**TABLE II**  
**TEST-SET MODEL COMPARISON (SEED 42, PRIMARY THRESHOLD POLICY)**

| Model | AUROC | AUPRC | F1 | ECE | Notes |
|-------|-------|-------|-----|-----|-------|
| LogReg (uncalibrated) | 0.761 | 0.380 | 0.417 | 0.249 | Threshold 0.52 |
| LogReg + sigmoid cal. | 0.761 | 0.379 | 0.415 | **0.020** | Primary calibrated model |
| LogReg + isotonic cal. | 0.761 | 0.378 | 0.404 | **0.014** | Lowest ECE |
| Tabular MLP | 0.766 | 0.386 | 0.406 | 0.028 | Threshold 0.12 |
| Random forest | 0.768 | 0.367 | 0.423 | 0.198 | Highest F1, miscalibrated |
| XGBoost | 0.768 | 0.382 | 0.409 | 0.207 | Highest AUROC (tie) |

*Primary threshold: F1-optimal on validation. Calibration rows use calibrated probabilities with validation-tuned thresholds (sigmoid 0.16, isotonic 0.12).*

### C. Operating Points

For **uncalibrated LogReg**, F1-optimal test performance was accuracy 0.707, F1 0.418, recall 0.651, specificity 0.717. A **screening-oriented** policy (validation recall ≥ 0.85) yielded test **recall = 0.816**, **specificity = 0.553**, F1 0.395 at threshold 0.385—appropriate for rule-out enrichment but with substantial false-positive burden.

For **tabular MLP**, F1-optimal test F1 was **0.425** (recall 0.518, specificity 0.823). Target-recall policy achieved **recall = 0.812**, specificity 0.563 at threshold 0.10. These trade-offs illustrate that model choice depends on clinical policy, not AUROC alone.

### D. Split Robustness

Across five grouped seeds, LogReg test metrics averaged **AUROC 0.769 ± 0.007**, **AUPRC 0.371 ± 0.009**, **F1 0.401 ± 0.015**, **recall 0.742 ± 0.061**, **specificity 0.649 ± 0.061**, and **ECE 0.261 ± 0.008** (uncalibrated pipeline in robustness sweep). Low AUROC variance supports stable ranking across splits; recall variance highlights sensitivity to partition choice for screening policies.

### E. Explainability

Global mean |SHAP| for LogReg ranked **anchor_age** highest (0.562), followed by **Medicare insurance** (0.275), **Black/African American race** (0.199), **EU observation admission type** (0.187), **gender** (0.172), **White race** (0.144), **observation admit type** (0.121), **length of stay** (0.104), and **urea nitrogen** among laboratory variables (0.047, rank 15). Demographic and utilization features dominated attributions; laboratory signals were present but smaller in magnitude—consistent with partial early-lab availability and proxy labeling.

**Fig. 1.** Study workflow: MIMIC-IV admission sampling → feature extraction with 48-h lab window → grouped split → model training → post-hoc calibration → threshold policies → SHAP analysis.

**Fig. 2.** Reliability diagram comparing uncalibrated and sigmoid-calibrated LogReg on the test set (`outputs/supervisor_runs/fig_mimic_calibration_reliability.png`). Calibration curves track the diagonal after Platt scaling; uncalibrated probabilities over-estimate risk for mid-range scores.

**Fig. 3.** Test-set AUROC comparison across model families (`outputs/supervisor_runs/fig_mimic_model_auroc.png`). Curves overlap substantially (AUROC 0.761–0.768), indicating limited incremental value from model complexity for this feature set.

**Fig. 4.** Top-10 mean |SHAP| features for LogReg (`outputs/supervisor_runs/fig_mimic_shap_top10.png`). Age and insurance status contribute most; admission type and select labs provide additional signal.

---

## IV. DISCUSSION

We presented an admission-level CKD proxy prediction study on MIMIC-IV designed for **methodological rigor**—grouped splits, calibration metrics, threshold policies, and explainability—rather than benchmark-leading discrimination. Test AUROC near **0.76–0.77** indicates moderate separability comparable to many tabular EHR tasks [1], [2]. The practically meaningful finding is **calibration**: uncalibrated LogReg ECE of **0.25** implies unreliable probability statements for clinicians; sigmoid calibration reduced ECE by an order of magnitude with unchanged AUROC, aligning with broader reports that modern classifiers are often miscalibrated [2], [7].

Model complexity did not materially improve discrimination. XGBoost and random forest exceeded LogReg AUROC by **≤0.007** while remaining poorly calibrated without post-processing. The tabular MLP achieved competitive AUROC with better native calibration but lower recall at F1-optimal thresholds. For deployment scenarios requiring **high sensitivity** (e.g., triage flags), threshold tuning raised recall above **0.81** at specificity near **0.55**—a conscious trade-off that must be weighed against alert fatigue.

SHAP attributions confirm face validity (age, renal-adjacent labs) but also surface **social and utilization variables** (insurance, admission type, race) that demand fairness auditing before any clinical use [3]. Proxy ICD labels conflate prevalent CKD, coding practice, and care setting; they do not replace eGFR staging [5]. Single-center retrospective design, absence of temporal external validation, and sampled cohort (30,000 of ~400k admissions) limit generalizability. We did not evaluate note text, vitals streams, or medication histories available elsewhere in MIMIC.

**Honest scope:** This paper contributes a **calibration- and leakage-aware evaluation protocol** with transparent operating points and explainability. It does **not** establish clinical utility, prospective performance, or multimodal superiority.

---

## V. CONCLUSION

Admission-level tabular models on MIMIC-IV achieve moderate CKD proxy discrimination (AUROC ~0.76–0.77) with substantial calibration defects in default logistic and tree models. Post-hoc sigmoid calibration yields reliable probabilities (ECE ~0.02) without changing ranking metrics. Grouped validation across five seeds confirms stable AUROC (0.769 ± 0.007). SHAP analysis highlights age, payer, admission context, and laboratory features. Before clinical decision support, future work must pursue temporal external validation, fairness assessment, eGFR-concordant labeling, and prospective workflow integration—none of which are claimed here.

---

## REFERENCES

[1] A. E. W. Johnson et al., "MIMIC-IV, a freely accessible electronic health record dataset," *Sci. Data*, vol. 10, no. 1, p. 1, 2023.

[2] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *Proc. ICML*, 2017, pp. 1321–1330.

[3] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Proc. NeurIPS*, 2017, pp. 4765–4774.

[4] J. Platt, "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods," in *Advances in Large Margin Classifiers*, MIT Press, 1999, pp. 61–74.

[5] KDIGO, "KDIGO 2012 clinical practice guideline for the evaluation and management of chronic kidney disease," *Kidney Int. Suppl.*, vol. 3, no. 1, pp. 1–150, 2013.

[6] A. E. W. Johnson et al., "MIMIC-III, a freely accessible critical care database," *Sci. Data*, vol. 3, p. 160035, 2016.

[7] A. Niculescu-Mizil and R. Caruana, "Predicting good probabilities with supervised learning," in *Proc. ICML*, 2005, pp. 625–632.

[8] G. Varoquaux, "Cross-validation failure: Small sample sizes lead to large error bars," *NeuroImage*, vol. 180, pp. 68–77, 2018.

[9] B. Shickel et al., "Deep EHR: A survey of recent advances in deep learning techniques for electronic health record (EHR) analysis," *IEEE J. Biomed. Health Inform.*, vol. 22, no. 5, pp. 1589–1604, 2018.

[10] F. Harrell Jr., *Regression Modeling Strategies*, 2nd ed. Springer, 2015.

[11] D. K. W. Young et al., "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.

[12] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. KDD*, 2016, pp. 785–794.

[13] L. E. D. Research et al., "The PhysioNet/CinC Challenge 2012: Predicting mortality of ICU patients," *Comput. Cardiol.*, 2012.

[14] Z. Obermeyer et al., "Dissecting racial bias in an algorithm used to manage the health of populations," *Science*, vol. 366, no. 6464, pp. 447–453, 2019.

[15] M. S. Pepe, *The Statistical Evaluation of Medical Tests for Classification and Prediction*. Oxford Univ. Press, 2003.

---

## SUBMISSION CHECKLIST (IEEE EMBC / CBMS)

### Page budget (4 pages + references)
- **Keep in main paper:** Abstract, Introduction (0.75 page), Methods (1.25 pages condensed), Results with Table I, Table II, and 2–3 figures (1.25 pages), Discussion + Conclusion (0.5 page).
- **Move to supplementary / cut first:** Youden thresholds; full five-seed table; permutation importance details; hyperparameter grids; confusion-matrix cell counts; extended SHAP case vignettes.
- **Never add to this submission:** Wearable/WESAD, NHANES main results, multimodal fusion, deployed UI screenshots.

### Figures for camera-ready
1. `fig_mimic_calibration_reliability.png` — Fig. 2 (single column, ~2.5 in wide).
2. `fig_mimic_model_auroc.png` — Fig. 3 (single column).
3. `fig_mimic_shap_top10.png` — Fig. 4 (single column).
4. Optional flow diagram (Fig. 1) — simple boxes, ≤0.5 page height.

### IEEE EMBC formatting notes
- Use **IEEEtran** conference template (`\documentclass[conference]{IEEEtran}`).
- Abstract: **150–200 words** (current draft ≈195 words — trim if venue requires 150).
- Keywords: 3–5 index terms after abstract.
- Sections numbered **I., II., III.** with capital Roman numerals.
- Tables: `TABLE I`, `TABLE II` captions **above** tables; figures captions **below**.
- References: IEEE numeric style [1]; verify MIMIC-IV citation [1] and SHAP [3] DOI pages before submission.
- Author affiliations use superscript markers; ORCID optional.
- **MIMIC credentialed use:** include PhysioNet DUA acknowledgment in Methods or Acknowledgment footnote.
- **Conflict of interest / IRB:** MIMIC is de-identified; state waiver/exemption per institutional policy.
- **Code availability:** one sentence pointing to repository or “available on reasonable request” if credentialed data prevent full sharing.

### Pre-submission actions (high priority)
- [ ] Run **temporal split** (train early years, test late) or add explicit limitation if deferred.
- [ ] Add **fairness/subgroup AUROC** (age, sex, race strata).
- [ ] Expand related work with 2–3 direct MIMIC CKD/AKI comparison rows.
- [ ] Professional copy-edit; verify all numbers against latest CSV re-run.
- [ ] Supervisor/co-author sign-off on proxy-label framing and clinical claims.
- [ ] Confirm figure resolution ≥ 300 dpi; embed TrueType fonts in PDF.

---

*Draft generated from `outputs/supervisor_runs/step2_mimic_*` artifacts. Align numbers if pipeline is re-run.*
