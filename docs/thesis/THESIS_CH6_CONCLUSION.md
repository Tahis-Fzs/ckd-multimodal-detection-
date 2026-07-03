# Chapter 6 — Conclusion (draft for DIU thesis / pre-defense)

Paste into Word Chapter 6 (merge with §6.2 Limitations from `THESIS_6_2_LIMITATIONS.md`).

---

## 6.1 Summary of Contributions

This thesis presented an explainable **multimodal learning framework** for early **CKD-related risk assessment**, integrating population clinical data (NHANES), hospital electronic health records (MIMIC-IV), and wearable physiology proxies (WESAD), with SHAP-based interpretability and a prototype clinical decision-support interface.

The **primary empirical contribution** is the **MIMIC admission-level branch**: subject-grouped evaluation, comparison of classical and tabular deep models, **sigmoid-calibrated logistic regression** as the locked primary model (`logreg_sigmoid_cal`, threshold 0.16), and test performance of AUROC **0.7614** with ECE **0.0203**. This demonstrates that hospital risk outputs can be both **discriminative and well-calibrated** for research decision support.

Secondary branches establish **population feasibility** (NHANES, separate cohort) and **wearable encoding feasibility** (WESAD stress proxy). A **late-fusion protocol** documents how branch probabilities could be combined when same-patient multimodal CKD data become available.

Deliverables include a reproducible supervisor notebook, modular `src/` code, frozen artifacts, thesis figures, and a Streamlit CDS prototype.

---

## 6.2 Limitations

*(Insert full text from `THESIS_6_2_LIMITATIONS.md` — seven points condensed to four in Word if page-limited.)*

Key boundaries:
- No patient-level merge across NHANES, MIMIC, and WESAD.
- WESAD has no CKD labels.
- Primary model is **ML (calibrated logistic regression)**, not end-to-end deep learning on raw waveforms.
- Fusion is protocol/proxy evaluation, not proven multimodal CKD benefit.
- CDS prototype is research-only.

---

## 6.3 Future Work

1. **Linked multimodal CKD cohort** — prospective or single-health-system data with aligned EHR + wearable + labs.
2. **External validation** — train MIMIC model, test on eICU, UK Biobank, or held-out hospital.
3. **Waveform encoders** — CNN/Transformer on MIMIC-IV-ECG or wearable streams with CKD labels.
4. **NLP branch** — structured + discharge-note features (separate from tabular primary).
5. **Prospective CDS pilot** — IRB-approved usability study with nephrology stakeholders.
6. **Federated learning** — privacy-preserving multi-site training (out of current scope).

---

## 6.4 Closing Statement

The project delivers a **methodologically rigorous, honest, and reproducible** pathway from public multimodal data to calibrated, explainable CKD-related hospital risk estimation. It advances the thesis goal of a **deep-learning-ready multimodal framework** while reporting transparently that the **locked primary evidence** rests on **calibrated machine learning** on MIMIC tabular admissions, with wearable and fusion components scoped to their validated roles. External validation and aligned multimodal data remain the necessary next steps before any clinical deployment claim.

---

## Defence one-liner

> “We built a multimodal CKD risk framework with a calibrated, explainable MIMIC primary model (~0.76 AUROC, ECE ~0.02), documented population and wearable branches, and an honest fusion protocol—ready for extension when linked patient data exist.”
