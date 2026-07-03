# Chapter 1 — Introduction (draft for DIU thesis / pre-defense)

Paste into Word; adjust figure/table numbering to match your template.

**Supervisor:** Dr. Naznin Sultana  
**Signed title:** A Deep Learning Framework for Early Detection of Chronic Kidney Disease: Integrating Multi-Modal Data from Wearable Devices and Clinical Records with Explainable AI

---

## 1.1 Background

Chronic kidney disease (CKD) is a slowly progressive condition in which kidney function declines over time, reflected by reduced estimated glomerular filtration rate (eGFR) or evidence of kidney damage [2], [18]. Severity ranges from early asymptomatic stages to end-stage renal disease (ESRD), dialysis, and transplantation, with substantial clinical and economic burden [2]. CKD is common worldwide, frequently coexists with hypertension and type 2 diabetes, and is often undetected in early stages because symptoms may be absent [7], [18]. Early identification of decreased kidney function or albuminuria enables medication, dietary modification, and risk-factor management [17], [18]. Reliable early risk stratification therefore remains an important challenge in nephrology and preventive medicine.

Traditional screening relies on serum creatinine, eGFR (CKD-EPI), and urine albumin-to-creatinine ratio (ACR) [17]. These markers are clinically useful but are intermittent, influenced by hydration, muscle mass, and acute illness, and do not provide continuous monitoring between clinic visits [1], [7]. Artificial intelligence (AI) methods can model high-dimensional structured data and nonlinear relationships in electronic health records (EHR) [1], [13], [43]. However, many CKD prediction studies use a single data modality and do not integrate complementary wearable physiology [1], [13], [32], [35]. Structured clinical records combined with wearable signals for CKD remain under-explored [36].

A further limitation of many black-box models is limited interpretability and poorly calibrated probabilities, which reduces trust in clinical decision support [46], [49], [50]. Explainable AI (XAI) methods such as SHAP can support feature-level review, but calibrated probability outputs and decision-support framing remain underdeveloped for multimodal CKD pipelines [15].

This thesis proposes a **multimodal learning framework** that supports both **classical machine learning** and **tabular deep learning** models, with **probability-level late fusion** [6], [36] and **SHAP-based explainability** [15] for transparent decision support rather than autonomous diagnosis [1], [7], [11]. The **primary locked hospital model** is **sigmoid-calibrated logistic regression** on MIMIC-IV admissions; deep tabular models are trained and compared under the same protocol.

---

## 1.2 Motivation

CKD prevalence is rising while many at-risk patients are diagnosed only after substantial nephron loss [7]. Periodic laboratory testing cannot monitor patients continuously between visits [1]. Risk prediction must address high-dimensional sparse features, class imbalance, heterogeneous data sources, and—critically—the absence of a public same-patient cohort linking hospital EHR, population surveys, and wearable recordings.

Wearable devices measure blood volume pulse (BVP), electrodermal activity (EDA), and skin temperature, which relate to autonomic and cardiovascular physiology relevant to chronic disease monitoring [32], [35]. Combining structured EHR features with wearable-derived summaries may enrich risk assessment, but engineering challenges include proxy labeling, cross-dataset generalization, and mismatched sampling rates.

From a clinical perspective, validated early risk tools may help identify high-risk patients before overt symptoms [18], [43]. From a technical perspective, this project delivers a reproducible pipeline with calibration, explainability, and a prototype decision-support interface for research evaluation.

---

## 1.3 Objectives

The aim is to develop an explainable **machine-learning and deep-learning framework** for early CKD-related risk assessment using structured clinical data and wearable physiology proxies, producing a **clinical decision-support prototype**, not an autonomous diagnostic system.

1. Prepare and preprocess CKD-relevant clinical data from **NHANES** and **MIMIC-IV**, including feature selection, missing-value handling, leakage removal, label construction, and grouped train/validation/test splitting.
2. Extract wearable physiological features from **WESAD** using window-based signal processing for the wearable branch.
3. Develop and compare branch-level models: logistic regression (with calibration), random forest, XGBoost, tabular MLP, and residual MLP.
4. Evaluate models using AUROC, AUPRC, F1-score, sensitivity, specificity, balanced accuracy, Brier score, and expected calibration error (ECE).
5. Implement explainability using feature importance and **SHAP** for clinically reviewable attributions.
6. Design **late fusion** combining branch-level probability outputs under the constraint that **no same-patient aligned multimodal CKD cohort** is available.
7. Develop a **prototype decision-support interface** presenting calibrated risk and explanations for demonstration and research evaluation.

---

## 1.4 Methodology

Three public datasets were used as **independent branches**: NHANES (population clinical) [6], MIMIC-IV v3.1 hospital EHR [30], and WESAD (wearable physiology) [16]. Each source was preprocessed separately; CKD-related or proxy labels were defined per branch; grouped splits prevented subject-level leakage [17], [18]. Clinical tabular features and wearable window statistics were extracted. Supervised models—including logistic regression with probability calibration, random forest, XGBoost, and PyTorch tabular MLPs—were trained per branch. **Late fusion** combined calibrated branch probabilities using validation-quality weights and a meta-logistic-regression comparator [36]. SHAP explainability was applied to the primary MIMIC model [15], [48]. Performance was assessed using discrimination, calibration, robustness, and temporal hold-out within MIMIC.

**Important:** datasets were **not merged at patient level**. Multimodal integration is **late fusion at probability level**, with proxy evaluation where aligned cohorts are unavailable.

---

## 1.5 Project Outcome

The project delivers a reproducible early CKD **risk-assessment framework** for research and decision support, not autonomous diagnosis.

**Primary MIMIC-IV test set** — locked model **`logreg_sigmoid_cal`**, threshold **0.16**:

| Metric | Value |
|--------|-------|
| Accuracy | 69.23% |
| AUROC | 0.7614 |
| F1 | 0.4145 |
| Sensitivity | 0.6739 |
| Specificity | 0.6959 |
| ECE | 0.0203 |

**NHANES branch** (separate cohort) — best model **XGBoost**: accuracy 96.60%, AUROC 0.9922, F1 0.7975. Not directly comparable to MIMIC.

**WESAD branch** (stress vs baseline proxy, not CKD-labeled): accuracy 81.21%, AUROC 0.7639, F1 0.6667.

A **late-fusion protocol** was implemented; because sources are not same-patient aligned and WESAD has no CKD labels, fusion is an **exploratory research outcome**, not a clinically validated multimodal CKD system.

Deliverables: reproducible pipeline, branch models, calibrated primary hospital model, SHAP explainability, fusion protocol, prototype CDS UI, and thesis figures under `paper_assets/`.

---

## 1.6 Organization of the Report

- **Chapter 1** introduces CKD, motivation, objectives, methodology, outcomes, and report structure.
- **Chapter 2** reviews literature and gap analysis (single modality, interpretability, multimodal integration).
- **Chapter 3** describes data acquisition, preprocessing, modeling, fusion, explainability, and evaluation.
- **Chapter 4** presents implementation and results (NHANES, MIMIC primary, WESAD, fusion, UI).
- **Chapter 5** discusses engineering standards, privacy, ethics, and reproducibility.
- **Chapter 6** concludes with contributions, limitations, and future work.

*Draft source:* `docs/thesis/THESIS_CH4_RESULTS_DRAFT.md`, `outputs/supervisor_runs/final_reporting_lock.json`.
