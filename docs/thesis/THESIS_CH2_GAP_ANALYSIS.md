# Chapter 2 — §2.3 Gap Analysis (draft for report)

**Paste into:** Chapter 2, Section 2.3, after §2.2 Similar Applications.  
**Table number:** Table 2.3 (adjust if your report already uses 2.3 for something else).

---

## 2.3 Gap Analysis

Despite substantial progress in machine learning for chronic kidney disease (CKD) screening and hospital risk prediction, a review of the literature and of comparable clinical decision-support prototypes reveals several gaps that motivate this project. Most published work focuses on a **single data modality** (survey laboratories, admission electronic health records, or wearable signals) and reports **discrimination metrics** (e.g., AUROC) without jointly addressing **leakage-aware evaluation**, **probability calibration**, **explainability**, and a **multimodal integration pathway**. Table 2.3 summarizes the identified gaps, limitations in existing approaches, the proposed response in this thesis, and how the implemented work addresses each deficiency—within the honest scope of disjoint public cohorts.

---

### Table 2.3: Gap Analysis — Identified Limitations and Proposed Solutions

| Gap ID | Identified gap | Limitation in existing work | Proposed solution (this thesis) | How this work addresses it |
|--------|----------------|----------------------------|----------------------------------|----------------------------|
| **G1** | **Fragmented multimodal CKD pipelines** | CKD prediction studies typically use one source: population surveys (e.g., NHANES-style biochemistry), hospital EHR tabular features, or physiological wearables. Few works present a **unified framework** that defines how clinical records, population data, and wearable encoders connect for early detection with explainability. | A **multimodal deep-learning framework** with three explicit branches (NHANES clinical, MIMIC hospital EHR, WESAD wearable encoder) and a documented late-fusion protocol (§14). | NHANES (§1–10), MIMIC (§12+), and WESAD (§16) are implemented as separate, reproducible pipelines under one supervisor notebook and architecture narrative. Fusion cells specify tensor shapes, alignment assumptions, and evaluation status without overstating same-patient validation. |
| **G2** | **Information leakage in hospital ML evaluation** | Many MIMIC-based studies split admissions **randomly**, allowing the same patient (`subject_id`) in train and test. This inflates performance and is inappropriate for admission-level CDS. | **Subject-level grouped splits** for MIMIC: all admissions from one patient stay in one partition; multi-seed robustness where reported. | MIMIC Step-2 uses grouped train/validation/test partitions on 30,000 admissions. Five-seed stability and bootstrap intervals support internal validity. Primary locked model: `logreg_sigmoid_cal`. |
| **G3** | **Miscalibrated risk probabilities** | Classifiers with acceptable AUROC often produce **unreliable probabilities** (high expected calibration error), limiting clinical interpretation of “% risk” outputs. | **Post-hoc calibration** (sigmoid / isotonic on validation) with ECE, Brier score, and reliability diagrams; explicit **threshold policies** (e.g., F1-optimal vs screening-oriented). | Uncalibrated logistic ECE ≈ **0.25** vs sigmoid-calibrated ECE ≈ **0.02** at similar test AUROC (~**0.76**). Threshold **0.16** frozen from validation policy. Calibration figure exported to `fig_mimic_calibration_reliability.png`. |
| **G4** | **Limited explainability for admission-level CDS** | Black-box models (deep nets, ensembles) are common; **per-admission attributions** and **global feature importance** are not always reported alongside calibration. | **Explainable AI layer**: permutation importance, SHAP on held-out MIMIC test set, and local logistic contributions in the CDS prototype. | Global SHAP top features (e.g., `anchor_age`, insurance, admission type) saved to `step2_mimic_shap_top15.csv` / `fig_mimic_shap_top10.png`. Streamlit prototype shows per-admission local explanations and frozen global SHAP summary. |
| **G5** | **Gap between offline models and demonstrable CDS** | Research pipelines often stop at offline metrics with no **interface** showing calibrated risk, thresholding, and interpretability for stakeholders. | **Research CDS prototype** (`demo_app.py`) loading frozen MIMIC artifacts: calibrated probability, adjustable threshold, example admission browse, manual entry, global SHAP tab. | Runnable Streamlit app documented in `UI_RUN.md`; thesis screenshots in `outputs/supervisor_runs/fig_ui_*.png`. Explicit disclaimer: research demonstration only, not clinical deployment. |
| **G6** | **Unvalidated same-patient multimodal fusion** | True multimodal CKD studies require **aligned modalities per patient**. Public disjoint datasets (NHANES, MIMIC, WESAD) cannot prove fusion improves individual-patient CKD detection without linkage. | **Transparent fusion protocol** (§14D–14E): late fusion design, proxy holdout evaluation, and explicit **non-claim** of clinical fusion benefit; limitations in §6.2. | Fusion meta-evaluation documented as protocol/demo (~AUROC 0.50 on proxy holdout). Thesis states fusion as **architectural contribution** and future-work enabler, not as evidence that wearables improved MIMIC CKD AUROC. |

---

### Narrative closing (after Table 2.3)

The gap analysis shows that this project does not claim a new state-of-the-art AUROC on a single benchmark. Instead, it targets a **valid and under-served subset** of the CKD machine-learning problem space: **reproducible, leakage-aware, calibrated, and explainable hospital risk stratification**, embedded in a **multimodal framework** with population and wearable branches and an honest treatment of fusion limits. The **primary empirical contribution** for title defence is the **MIMIC clinical branch** (G2–G5); NHANES and WESAD support generalizability of the framework design (G1); G6 bounds what fusion can and cannot be claimed before linked multimodal CKD data become available.

---

## Word formatting notes

1. In Word, use **Insert → Table** with 5 columns; copy row text from the markdown table above.
2. Set **Table 2.3** caption: *Gap Analysis — Identified Limitations and Proposed Solutions*.
3. Keep **Gap ID** column narrow (G1–G6).
4. If page space is tight, merge G1+G6 into one row titled *Multimodal integration without same-patient linkage* and reduce to **five rows**—substance unchanged.

---

## Mapping to thesis chapters

| Gap | Primary evidence chapter | Key artifact |
|-----|--------------------------|--------------|
| G1 | Ch. 3 (methodology), Ch. 4 (results §4.1–4.3) | Supervisor notebook branches |
| G2 | Ch. 4.2 (MIMIC) | Grouped split spec, `final_reporting_lock.json` |
| G3 | Ch. 4.2 | `step2_mimic_calibration_summary.csv`, calibration figure |
| G4 | Ch. 4.2, Ch. 4.5 (UI) | SHAP CSV/figures, `demo_app.py` |
| G5 | Ch. 4.5, Ch. 5 | UI screenshots, `UI_RUN.md` |
| G6 | Ch. 4.4, §6.2 Limitations | `fusion-assumptions` / §14 outputs, limitations draft |

---

## Defence one-liner (if asked “what gap do you fill?”)

> “Existing CKD hospital ML often ignores grouped splits, calibration, and explainability together, and multimodal work rarely documents what can be validated on disjoint public data—we deliver a calibrated, explainable MIMIC branch inside a multimodal framework, with fusion scoped honestly as protocol, not proven clinical benefit.”
