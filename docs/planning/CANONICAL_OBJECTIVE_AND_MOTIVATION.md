# Canonical objective and motivation (use this text across all documents)

Use the **same wording** in the thesis introduction, methodology overview, README-style notes, and any slide or appendix that describes the project. Adjust only the **subsection title** or one sentence if a document is *only* about the supervisor notebook (then emphasize §3).

---

## 1. Motivation

Chronic kidney disease (CKD) is often recognized late, while routine clinical and demographic data already contain signals of reduced kidney function. Early risk stratification could support better follow-up and resource use, but models must be evaluated with **rigorous splits**, **discrimination and calibration**, and **clear scope** (risk prediction and interpretation, not treatment advice). Public datasets make this research reproducible without accessing institutional patient records. The broader programme also targets **multimodal** information (structured records and physiology from wearables or waveforms) and **explainable AI** so that predictions can be scrutinized in line with clinical expectations.

---

## 2. Overall thesis objective (signed title; unchanged for registry and high-level chapters)

**Objective:** Develop a **deep learning framework oriented to early CKD detection** that can integrate **multi-modal** evidence—**clinical / EHR-style records** and **wearable or waveform-derived physiology**—and support **explainable AI**, within the constraints of **public data** and a **prototype clinical decision support** framing (visualization of risk and explanations; **no therapeutic recommendations**).

This sentence is aligned with the official title:

*A Deep Learning Framework for Early Detection of Chronic Kidney Disease: Integrating Multi-Modal Data from Wearable Devices and Clinical Records with Explainable AI.*

---

## 3. Objective and scope of the **implemented supervisor pipeline** (code-accurate)

The notebook **`CKD Dataset/ckd_supervisor_pipeline_from_scratch.ipynb`** and its saved outputs under **`CKD Dataset/outputs/supervisor_runs/`** implement the following **concrete** objectives (this is what the code does today):

1. **NHANES (2013–2014, tabular):** Build a **clinically defined** CKD-relevant label from harmonized tables; engineer **leakage-aware** numeric features; split by **`SEQN`** (no subject in both train and test); **median-impute** and **standardize** using train-only statistics; compare **balanced logistic regression**, a **tabular MLP**, and a **residual MLP**; report **AUROC, AUPRC, F1, calibration-related metrics (e.g. ECE, Brier)**, and **operating thresholds** chosen on the validation split.

2. **MIMIC-IV (hosp, admission-level tabular):** Build a **within-MIMIC** cohort with a **CKD-related diagnosis proxy** (ICD-9 `585*`, ICD-10 `N18*`) and admission-level features (demographics / admission fields and **aggregated lab-derived** columns when `labevents` is available); split by **`subject_id`**; apply the same preprocessing discipline; compare **logistic regression** and a **tabular MLP**; report the same style of metrics.

3. **Cross-dataset fusion (documented layer):** NHANES and MIMIC are **not linked by patient ID**. Step 3 records a **late fusion / weighting protocol** from **branch-level** performance (see `step3_fusion_spec.csv` and `step3_fusion_protocol.json`), not a single joint training cohort across sites.

**Explicit non-claims for this repository snapshot:** End-to-end training of **WESAD**, **MIMIC-IV-ECG** waveforms, **Transformers on longitudinal ICU sequences**, or a **deployed CDS UI** is **not** required to be present in the supervisor notebook for the above bullets to remain true. Those elements remain **thesis-level architecture** and future or parallel work unless another chapter points to corresponding code.

---

## 4. One-paragraph merge (optional “abstract style” block)

Chronic kidney disease is often identified late despite information in routine data. This work aims toward a **multimodal, explainable deep learning framework for early CKD risk** consistent with the signed project title. In the **current codebase**, we instantiate part of that vision as **reproducible tabular pipelines** on **NHANES** and **MIMIC-IV** with **grouped train/validation/test splits**, **train-only preprocessing**, **classical and deep tabular models**, **discrimination and calibration-oriented metrics**, and a **documented fusion protocol** across branches **without cross-cohort patient linkage**—providing an evaluation backbone that broader multimodal and XAI components can extend.

---

## 5. Where to paste

| Location | Use |
|----------|-----|
| Thesis Ch. 1 (Introduction) | §1 Motivation + §2 Overall thesis objective; add §3 if this chapter also describes the notebook. |
| Thesis Ch. 3 / Methods (implementation) | §3 verbatim as “scope of implemented pipeline.” |
| `SUPERVISOR_PIPELINE_OUTPUT_SUMMARY.md` | Short pointer: “Objectives and motivation: see `CANONICAL_OBJECTIVE_AND_MOTIVATION.md`.” |
| Architecture / XAI protocol markdown in repo | Keep technical detail there; **do not contradict** §2–§3 above. |
| Slides / defence | Prefer §4 one-paragraph merge, or §1 + one sentence from §2. |

---

*Last aligned to: `ckd_supervisor_pipeline_from_scratch.ipynb` (outputs under `outputs/supervisor_runs/`) and `title-proposal-alignment.md`.*
