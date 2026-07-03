# Explainability (XAI) protocol: EHR vs waveforms vs fusion

This document specifies **which method applies where**, how **train/validation/test** splits interact with explanations, and how to report results without over-claiming causality. It is aligned with the **Title Phase** objectives: SHAP, Grad-CAM, and attention weights; metrics **AUC-ROC**, **F1-score**, and **calibration**; and a **prototype clinical decision support** layer (visualization only — no therapeutic advice).

---

## 1. Branch-specific methods

### 1.1 Structured EHR / tabular path (NHANES, MIMIC-derived features)

| Method | When to use | Strengths | Caveats |
|--------|-------------|-----------|---------|
| **SHAP** | Default for **tree ensembles** (XGBoost, LightGBM, RF) on harmonized features; also **DeepSHAP** / gradient-based SHAP for neural nets on tabular input | Consistent global + local attributions; strong for ranking feature importance | Correlated features can split importance; compute cost for large backgrounds |
| **LIME** | **Sparse** local explanations around one prediction; useful when the model is **non-smooth** or SHAP is too costly | Fast local “why this patient” narratives | Instability across perturbations; sensitive to kernel width and neighborhood |

**Recommendation:** Prefer **SHAP** for the primary EHR model if it is tree-based or a standard MLP on fixed features; use **LIME** as a **secondary** check for a handful of case studies (e.g., high-risk false positives/negatives) where you want a narrative paragraph in the thesis.

**Features to prioritize in reports:** creatinine, eGFR (or components), blood pressure, diabetes indicators, age, albuminuria if present—aligned with KDIGO-style reasoning, not only raw SHAP order.

### 1.2 Wearable / signal path (WESAD encoder)

| Method | When to use | Strengths | Caveats |
|--------|-------------|-----------|---------|
| **Attention weights** | Transformer or attention pooling over **time** or **channels** | Shows *when* or *which stream* mattered | Attention ≠ causation; can be diffuse |
| **Grad-CAM / Grad-CAM++** | CNN over **spectrograms** or 2D time–channel maps | Spatial localization on the input tensor | Must match the target convolutional layer; verify with a sanity check (randomized weights) |
| **Saliency / integrated gradients** | 1D CNN or raw waveform models | Fine-grained temporal sensitivity | Noisy; smooth inputs or integrated gradients help |

**Recommendation:** Report **one primary** wearable explanation method (e.g., Grad-CAM on the CNN trunk **or** temporal attention) plus **one qualitative figure** per modality (ECG vs EDA vs temp) if channels are separable.

**MIMIC-IV-ECG (12-lead clinical waveforms):** Use the same toolkit (**temporal attention**, **Grad-CAM** on a 2D lead×time map, or **integrated gradients** on 1D-per-lead stacks). Fixed 12-lead layout often makes **lead-level** attribution easier to narrate than mixed wearable channels; stay explicit that explanations reflect **model sensitivity**, not a standalone cardiology diagnosis.

### 1.3 Fusion layer

- If fusion uses **cross-attention** or **gating** among **z_ehr**, **z_ecg**, and **z_wear**, report **attention weights or gate values** as “which modality contributed more to this embedding mix,” with explicit disclaimer that this is **not** a clinical causal statement.
- Optional: **SHAP on the small MLP head** after fusion if the head is shallow and inputs are the embeddings (interpret as **modality-level** influence, not raw labs).

### 1.4 Prototype clinical decision support (CDS)

The signed proposal calls for a **prototype interface** to visualize predictions and interpretability outputs (similar in spirit to trajectory-oriented CDS such as TrajVis in your references). In scope:

- **Inputs to the UI:** fused model output (CKD risk score or class), **SHAP** (or LIME) summary for EHR features, **attention or Grad-CAM** snapshots for **MIMIC-IV-ECG** and/or **WESAD** branches when present.
- **Out of scope:** treatment recommendations, dosing, or live EMR integration — consistent with the Title Phase **scope of work**.

---

## 2. Discrimination and calibration (Title Phase metrics)

Report alongside XAI:

| Metric | Role |
|--------|------|
| **AUC-ROC** | Discrimination (primary benchmark vs literature) |
| **F1-score** | Balance when classes are imbalanced |
| **Calibration error** | Reliability of predicted probabilities — e.g., **Expected Calibration Error (ECE)**, Brier score, reliability diagrams (compare **before/after** temperature scaling or isotonic regression on a validation fold) |

Well-calibrated risk scores matter for clinical-facing narratives even when the thesis prototype does not connect to real hospitals.

---

## 3. Data splits and XAI (avoid leakage)

1. **Fit** any background distribution for SHAP (e.g., k-means summary of training data) **only on the training split**.
2. **LIME** neighborhoods: fit the interpretable surrogate using **only** training-set statistics where applicable; explain **validation/test** patients as hold-out cases.
3. **Grad-CAM / attention:** compute on **held-out** windows or patients reserved for testing; do not tune architecture choices to maximize explanation “prettiness” on test.
4. Report **separate** EHR-only vs **EHR+wearable** metrics on the **same** test protocol when comparing explainability (e.g., same patient order where both modalities exist, or matched simulation).

---

## 4. What to put in the thesis / defence (minimal checklist)

- One **global** EHR figure: mean |SHAP| (or SHAP summary plot) on the **test** set or a stratified subset.
- One **local** EHR figure: SHAP force or LIME for **one** clinically interesting case.
- One **wearable** figure: Grad-CAM or attention on **one** representative window (label the time axis and sensor).
- One sentence on **limitations**: associative modeling, shift across NHANES vs MIMIC vs WESAD, no causal claims from XAI alone.
- One **calibration** figure (reliability curve or ECE before/after calibration) on held-out data.
- One **CDS mock-up** screenshot: risk + SHAP + signal explanation (if wearable used).

---

## 5. Evaluation split (aligned with modeling)

| Cohort | Typical role | XAI usage |
|--------|----------------|-----------|
| NHANES train/val | Structured CKD labels | SHAP/LIME background from train; global plots on val |
| MIMIC-IV train/val | Temporal EHR | Same; optionally domain-specific SHAP strata |
| WESAD | Encoder pretraining only | Grad-CAM/attention on WESAD **test windows** (no CKD label) |
| Held-out test (per cohort) | Final AUC / calibration | Local explanations on **test** patients only |

If **no subject has both EHR and wearable** in public data, state clearly that **fusion XAI** is demonstrated on **synthetic pairing**, **subset studies**, or **deployment scenario simulation**, not on a real paired cohort unless you obtain one.
