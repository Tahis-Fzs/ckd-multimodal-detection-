# Pre-defense slides outline (10–15 slides)

Copy bullets into PowerPoint / Google Slides. Figures from `paper_assets/figures/`.

---

## Slide 1 — Title
- **A Deep Learning Framework for Early Detection of Chronic Kidney Disease**
- Multimodal clinical + wearable data with explainable AI
- Md. Shadman Tahsin · DIU CSE · Supervisor: Dr. Naznin Sultana

---

## Slide 2 — Problem
- CKD often silent until advanced stages
- Need early **risk stratification**, not only lab snapshots
- Gap: single-modality models, poor calibration, limited XAI, weak multimodal integration

---

## Slide 3 — Objectives
- NHANES + MIMIC + WESAD branches
- Compare ML + tabular DL models
- Calibrate + explain + prototype CDS
- Late fusion **protocol** (honest scope)

---

## Slide 4 — Architecture (diagram)
- Three towers → branch probabilities → late fusion → CDS UI
- Use `paper_assets/diagrams/architecture-diagram.mmd` or draw simplified version
- **Note:** no same-patient merge across public datasets

---

## Slide 5 — Datasets
| Branch | Source | Label |
| NHANES | Population survey | eGFR CKD proxy |
| MIMIC | Hospital EHR | ICD CKD proxy |
| WESAD | Wearable | Stress proxy (not CKD) |

---

## Slide 6 — Methodology (MIMIC primary)
- 30k admissions, 68 tabular features, 48h labs
- Grouped split by `subject_id`
- Models: LogReg, RF, XGB, MLP
- Sigmoid calibration + SHAP

---

## Slide 7 — Primary result ★
- Model: **logreg_sigmoid_cal**, threshold **0.16**
- AUROC **0.7614**, ECE **0.0203**
- Figure: `fig_mimic_calibration_reliability.png`

---

## Slide 8 — Model comparison
- Figure: `fig_mimic_model_auroc.png`
- Similar AUROC across families; calibration chose LogReg

---

## Slide 9 — Explainability
- Figure: `fig_mimic_shap_top10.png`
- Age, insurance, admission type, BUN among top features

---

## Slide 10 — Confusion matrix
- Figure: `fig_mimic_confusion_matrix_logreg_sigmoid_cal.png`
- Screening-oriented threshold 0.16

---

## Slide 11 — NHANES & WESAD (secondary)
- NHANES XGBoost AUROC ~0.99 — **separate cohort**
- WESAD RF AUROC ~0.76 — **wearable proxy only**
- Figure: `figure_3_6_wesad_window.png`

---

## Slide 12 — Fusion (honest)
- Late fusion protocol + proxy evaluation
- **Not** same-patient validated multimodal CKD
- Future: linked cohort required

---

## Slide 13 — CDS demo
- Screenshots: `fig_ui_*.png`
- `./run_cds_app.sh` — research prototype only

---

## Slide 14 — Limitations
- ML-primary, not raw-signal DL
- No patient-level merge
- WESAD not CKD-labeled
- No clinical deployment

---

## Slide 15 — Conclusion
- Reproducible calibrated MIMIC branch + multimodal framework
- Thank you / Q&A

---

## Demo backup
- Default admission: `hadm_id=24251211` (index 148)
- Memorize: AUROC 0.7614, ECE 0.0203, threshold 0.16
