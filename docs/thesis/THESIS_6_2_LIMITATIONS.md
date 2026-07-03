# Chapter 6 — Section 6.2 Limitations (draft for thesis)

Although the proposed framework demonstrates a reproducible multimodal pathway for CKD-related risk assessment, several limitations must be stated explicitly.

**First**, the primary hospital evaluation uses an **admission-level CKD proxy label** derived from ICD-9/ICD-10 diagnosis codes (585*, N18*) during the index hospitalization. This label reflects documented CKD during the stay and is **not equivalent** to KDIGO staging based on estimated glomerular filtration rate (eGFR) and albuminuria. Consequently, the MIMIC results should be interpreted as **risk stratification and early flagging**, not definitive CKD diagnosis or staging.

**Second**, **NHANES, MIMIC-IV, and WESAD are disjoint cohorts** with no shared patient identifiers. NHANES provides population-level survey and laboratory data; MIMIC provides hospital electronic health records; WESAD provides ambulatory physiological signals from a stress-physiology study. Therefore, **true same-patient multimodal fusion cannot be empirically validated** in this work. Step 3 fusion cells (§14D–14E) implement a **late-fusion protocol** using branch-level demonstration and simulated holdout data; they **do not** establish that combining modalities improves CKD detection for individual patients.

**Third**, the **wearable branch (WESAD)** does not contain CKD labels. The implemented task is **stress versus baseline physiology** on a small public wearable dataset (15 subjects). This branch demonstrates how continuous wrist/chest signals can be encoded and interfaced with the fusion architecture; it **must not** be interpreted as wearable-based CKD detection or as evidence that wearables improved CKD prediction in the main evaluation.

**Fourth**, **medical imaging** (renal ultrasound, MRI, or other modality-specific imaging) was **not** included in the implemented pipeline. Although the project title references multimodal clinical data broadly, the empirical work is limited to **tabular EHR/laboratory features** (NHANES, MIMIC) and **wearable time-series summaries** (WESAD). Hospital 12-lead ECG (MIMIC-IV-ECG) was identified as a future same-patient waveform complement but was **not** trained or evaluated in this thesis.

**Fifth**, **NHANES and MIMIC results are not directly comparable** as a single performance claim. NHANES uses eGFR-based labels on a curated biochemistry subset and achieves high discrimination on that cohort; MIMIC uses ICD proxy labels on admission-level tabular features with moderate discrimination (~76% AUROC) but stronger **calibration and explainability** reporting. These are **separate branches**, not a unified benchmark.

**Sixth**, the clinical decision-support prototype (`demo_app.py`) is a **research demonstration** loaded from frozen MIMIC artifacts. It is **not** deployed in a live hospital environment, has not undergone prospective clinical validation, and does not replace laboratory assessment (creatinine, eGFR, urinalysis).

**Seventh**, external validation is **partial**. Grouped cross-validation and multi-seed robustness address internal stability; temporal hold-out within MIMIC addresses one form of external validity. **Cross-database external validation** (e.g., eICU, UK Biobank, or NHANES as an external test of the MIMIC model) was outside the scope of this title-phase timeline.

**In summary**, this thesis delivers a **methodologically rigorous clinical branch on MIMIC**, supporting branches on NHANES and WESAD, and a **documented fusion protocol**. The limitations above define the boundary between what was **implemented and evaluated** versus what remains **architectural or future work**.
