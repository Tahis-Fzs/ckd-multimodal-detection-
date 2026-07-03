# Alignment: signed title proposal vs architecture

**Source:** [Title_Phase_Evaluation_Report (1461,1462).pdf](Title_Phase_Evaluation_Report%20(1461,1462).pdf) — FYDP Title Phase, Fall 2025. Supervisor: Dr. Naznin Sultana (signed certificate section).

## Official project title

**A Deep Learning Framework for Early Detection of Chronic Kidney Disease: Integrating Multi-Modal Data from Wearable Devices and Clinical Records with Explainable AI**

**Consistent motivation and objectives (thesis + code-aligned wording):** use [CANONICAL_OBJECTIVE_AND_MOTIVATION.md](CANONICAL_OBJECTIVE_AND_MOTIVATION.md) as the single canonical source across documents.

## What the proposal commits to

| Proposal element | Meaning for the architecture |
|------------------|------------------------------|
| **Multimodal:** wearables + clinical/EHR | EHR encoder (NHANES + MIMIC-IV); waveform encoders for **ambulatory** WESAD (**z_wear**) and **clinical 12-lead ECG** via MIMIC-IV-ECG (**z_ecg**, pairable with MIMIC); fusion at embedding level — [fusion-assumptions.md](fusion-assumptions.md). |
| **Deep learning fusion:** CNN–RNN hybrids or **Transformer-based** models | MIMIC-IV longitudinal sequences suit **RNN/Transformer** (background cites HERBERT); NHANES suits tabular or flattened features. The diagram should name Transformers explicitly on the EHR side. |
| **XAI:** SHAP, Grad-CAM, **attention weights** | Matches [xai-protocol.md](xai-protocol.md): SHAP/LIME on EHR; Grad-CAM/attention on signals; optional fusion-level attribution. |
| **Metrics:** AUC-ROC, F1, **calibration error** | Report discrimination **and** calibration (reliability curves, Brier score, ECE) — not only AUC/F1. |
| **Prototype clinical decision support interface** | Add an explicit **CDS / visualization** output layer: risk score + SHAP summary + (optional) signal attention maps — *simulated* integration per scope. |
| **Public wearable and EHR datasets** | NHANES, MIMIC-IV (± ED), **MIMIC-IV-ECG**, WESAD; document credentialing, licensing, and cohort limits. |
| **Scope:** prediction and interpretation **only**; **no therapeutic** recommendations | Architecture ends at risk stratification + explanations; no treatment policy head. |
| **No real-time hospital infrastructure** | “Real-time wearable” in the research question means **continuous signal modeling**, not live EMR deployment; prototype simulates hospital-style CDS. |

## Re-evaluation verdict

The existing **NHANES + MIMIC-IV + MIMIC-IV-ECG + WESAD + fusion + XAI** architecture remains **valid** for the signed title (MIMIC-IV-ED optional for acute EHR context). Gaps addressed by updates elsewhere in this folder:

1. **EHR branch** — Name **Transformer / HERBERT-style** encoders where MIMIC temporal data is used; keep NHANES as structured/tabular input to the same conceptual `z_ehr` after harmonization.
2. **Outputs** — Extend the conceptual diagram with **CDS prototype** (visualization of prediction + XAI), matching objective 6.
3. **Evaluation** — Add **calibration** to the reporting protocol alongside AUC-ROC and F1.
4. **Wording** — The proposal’s “real-time wearable device data” is consistent with **windowed continuous signals** (WESAD); avoid implying every subject has paired wearable + EHR in one merged cohort unless you obtain such data.

## Research question (sanity check)

*How can a multimodal deep-learning and Explainable AI framework improve early detection and risk prediction of CKD by integrating real-time wearable device data with clinical health records?*

**Architecture answer:** By learning **z_wear** from wearable streams and **z_ehr** from clinical records, fusing them for CKD risk, and exposing **interpretable** evidence (SHAP on clinical features; attention/Grad-CAM on physiology) through a **prototype CDS** — under public-data constraints and without treatment advice.
