# Chapter 5 — Engineering Standards and Design Challenges (draft for report)

**Paste into:** Chapter 5 of FYDP report.  
**Aligns with:** Rice FYDP template structure (§5.1–5.5, Tables 5.1–5.3).

---

## Chapter 5 — Engineering Standards and Design Challenges

This chapter describes the engineering practices adopted in this project, the societal and ethical context of a clinical decision-support research system, project management, and mapping to **complex engineering problem (EP)** and **engineering activity (EA)** criteria required by the CSE programme.

---

## 5.1 Compliance with the Standards

Only standards relevant to this project are discussed. For each, alternatives are noted briefly with rationale for selection.

### 5.1.1 Software Standards

| Standard / practice | Role in this project | Alternatives considered | Rationale for selection |
|---------------------|----------------------|-------------------------|-------------------------|
| **Python 3.12** (PEP 8 style) | End-to-end pipeline, Streamlit CDS, figure scripts | R-only biostatistics stack | Dominant ML/ecosystem; matches DIU curriculum and library support |
| **Jupyter Notebook** (`ckd_supervisor_pipeline_from_scratch.ipynb`) | Reproducible staged experiments (§1–16) | Plain scripts only, DVC pipelines | Supervisor-friendly stepwise execution; frozen artifacts exported to `outputs/supervisor_runs/` |
| **scikit-learn** | MIMIC primary models, imputation, scaling, calibration, grouped CV | TensorFlow-only, custom C++ | Mature tabular ML; `CalibratedClassifierCV`, `GroupKFold`; matches hospital EHR feature matrix |
| **PyTorch** (NHANES ResMLP branch, where used) | Neural baseline on survey biochemistry | sklearn MLP only | Flexible training for population branch; standard in deep-learning coursework |
| **Streamlit** | Research CDS prototype (`demo_app.py`) | Flask + React, Gradio | Rapid thesis demo; loads frozen pickle/CSV artifacts |
| **JSON / CSV / pickle artifacts** | Reporting lock, metrics, SHAP, checkpoints | SQL database, MLflow only | Lightweight, versionable outputs without deployment infrastructure |
| **Reproducibility conventions** | Fixed seeds, documented splits, `final_reporting_lock.json` | Ad-hoc notebook runs | Required for defensible thesis results and examiner audit |

**Note:** This is **research software**, not a regulated medical device. Standards such as IEC 62304 (medical device software lifecycle) are **acknowledged** but **not claimed** as fully implemented—appropriate for FYDP scope.

### 5.1.2 Hardware Standards

| Resource | Use | Notes |
|----------|-----|-------|
| **Development workstation** (macOS / Linux) | Notebook execution, Streamlit, plotting | Primary environment for title-phase work |
| **CPU + optional NVIDIA GPU** | NHANES/WESAD training; MIMIC tabular work is CPU-feasible | GPU accelerates neural branches; not mandatory for locked MIMIC logistic model |
| **Local storage** | MIMIC-IV subset, NHANES, WESAD, `outputs/supervisor_runs/` | Large gzip CSVs (e.g., `labevents.csv.gz`); disk planning required |
| **PhysioNet credentialed access** | MIMIC-IV download under DUA | Standard for hospital EHR research; ethics training completed |

Microscopic imaging hardware (Rice template) does **not** apply; this project uses **existing public clinical and wearable datasets**, not custom sensor acquisition.

### 5.1.3 Communication Standards

| Standard / pattern | Application |
|--------------------|-------------|
| **HTTP localhost (Streamlit)** | CDS prototype served on `localhost:8501` for demonstration |
| **REST-style design principles** (conceptual) | Future hospital integration would expose `/predict` APIs; not implemented in FYDP |
| **HL7 FHIR** (awareness) | EHR interoperability standard; cited as **future integration** path for admission features and lab codes—not implemented |
| **LOINC / ICD coding** | MIMIC labs and CKD proxy labels derived from diagnosis/lab itemids mapped in notebook |

---

## 5.2 Impact on Society, Environment and Sustainability

### 5.2.1 Impact on Life

Chronic kidney disease is often detected late, increasing morbidity and treatment cost. A **calibrated, explainable risk-stratification framework**—if validated prospectively in future work—could support earlier flagging during hospital admission and population screening contexts. This thesis delivers a **research prototype**, not a deployed clinical tool. Potential beneficiaries (indirect, future) include:

- **Nephrology and internal medicine clinicians** — decision support adjunct to creatinine/eGFR  
- **Hospital quality teams** — screening workflows on admission  
- **Public-health researchers** — reproducible multimodal methodology on open cohorts  
- **Patients** — indirect benefit only after rigorous validation and governance (out of scope here)

### 5.2.2 Impact on Society and Environment

- **Societal:** Supports **SDG 3 (Good Health and Well-being)** by advancing methods for early CKD-related risk awareness using EHR and wearable research pathways.  
- **Environmental:** Predominantly **digital/computational** work; environmental footprint is limited to electricity for model training. No wet-lab reagents or field deployment. Lightweight tabular models (primary MIMIC logistic branch) are **more energy-efficient** than large multimodal foundation models—an intentional engineering trade-off.  
- **Digital divide:** CDS UI is English-based; Bangladesh deployment would require localization and low-bandwidth design (future work).

### 5.2.3 Ethical Aspects

| Topic | How this project addresses it |
|-------|------------------------------|
| **Patient privacy** | MIMIC-IV and NHANES are de-identified public research datasets under data-use agreements; no live patient data collected |
| **Informed consent** | Relies on datasets whose consent models are defined by PhysioNet/CDC; no new human subjects protocol in this FYDP |
| **Bias and fairness** | EHR models reflect documentation bias (insurance, race, admission type appear in SHAP); reported, not corrected—limitation stated in §6.2 |
| **Clinical misuse** | Streamlit disclaimer: **not for clinical diagnosis**; probabilities are research demonstrations |
| **Transparency** | Calibration, SHAP, and limitations documented to reduce “black box” misuse |
| **Honest claims** | Fusion and WESAD branches not presented as proven CKD wearable detection |

### 5.2.4 Sustainability Plan

- **Modular branches** (NHANES, MIMIC, WESAD, fusion) allow independent updates when datasets refresh.  
- **Frozen artifacts** (`step2_mimic_checkpoint.pkl`, CSV metrics) enable thesis reproduction without full retrain.  
- **Open-source stack** avoids license lock-in.  
- **Future maintenance:** Swap MIMIC-IV version, add MIMIC-IV-ECG waveform branch, or link wearables when aligned CKD cohorts exist.

---

## 5.3 Project Management and Financial Analysis

### 5.3.1 Phases (summary)

| Phase | Name | Objectives | Key deliverable | Indicative period |
|-------|------|------------|-----------------|-------------------|
| **P1** | Research & planning | Literature review, gap analysis (Table 2.3), architecture | Requirements, dataset access | Early semester |
| **P2** | Data engineering | NHANES, MIMIC, WESAD ingest; feature windows; labels | Clean branch datasets | Mid semester |
| **P3** | Model development | NHANES models; MIMIC Step-2; WESAD encoder; fusion §14 | Checkpoints, `final_reporting_lock.json` | Mid–late semester |
| **P4** | Evaluation & XAI | Calibration, baselines, SHAP, confusion matrix, robustness | Figures in `outputs/supervisor_runs/` | Late semester |
| **P5** | Integration & thesis | Streamlit CDS, report chapters, defence prep | `demo_app.py`, FYDP report | Final weeks |

### 5.3.2 Financial analysis

| Item | Cost |
|------|------|
| Software (Python, scikit-learn, PyTorch, Streamlit) | **Free** (open source) |
| MIMIC-IV access | **Free** under PhysioNet credentialed researcher agreement |
| NHANES / WESAD | **Free** public downloads |
| Hardware | Existing laptop/workstation; optional GPU already owned |
| Cloud | **Not required** for locked thesis results |
| **Recurring deployment cost** | Not incurred (research prototype only) |

**Conclusion:** Development cost is primarily **student time + compute electricity**; no commercial licenses. Prospective hospital deployment would add hosting, security audit, and clinical validation costs—explicitly **out of scope**.

---

## 5.4 Complex Engineering Problem

### 5.4.1 Complex Problem Solving

**Table 5.1: Mapping with Complex Engineering Problem**

| EP1 Depth of knowledge | EP2 Range of conflicting requirements | EP3 Depth of analysis | EP4 Familiarity of issues | EP5 Extent of applicable codes | EP6 Stakeholder involvement | EP7 Interdependence |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |

---

**EP1 — Depth of knowledge**  
This project integrates **computer science** (ML pipelines, calibration, explainability, UI), **biomedical informatics** (MIMIC admission structure, ICD CKD proxies, lab time windows), and **physiological sensing** (WESAD wearable signals). No single undergraduate course covers all layers; the supervisor notebook synthesizes them into one framework.

**EP2 — Range of conflicting requirements**  
Key tensions resolved (or explicitly bounded) include:

- **Discrimination vs calibration** — High AUROC with unreliable probabilities (ECE ≈ 0.25 uncalibrated) vs sigmoid calibration (ECE ≈ 0.02).  
- **Screening sensitivity vs false alarms** — Low threshold (0.16) flags more positives; documented in calibration summary.  
- **Multimodal ambition vs data linkage** — Title promises multimodal integration; disjoint cohorts force **protocol-level** fusion, not proven patient-level benefit.  
- **Model complexity vs interpretability** — Primary lock on **logistic regression** for SHAP and clinical transparency vs heavier XGB/MLP baselines.  
- **Compute vs timeline** — Tabular MIMIC primary path chosen for reproducibility on student hardware.

**EP3 — Depth of analysis**  
Beyond AUROC alone: **AUPRC**, **Brier score**, **ECE**, reliability diagrams, **grouped splits by `subject_id`**, multi-seed stability, bootstrap CIs, confusion matrix at operating threshold, **global and local explainability**, and branch-specific limitations.

**EP4 — Familiarity of issues**  
CKD **KDIGO staging** (eGFR, albuminuria) differs from **ICD proxy labels** on admission. **Admission-window labs** are sparse (~5.6% creatinine coverage). **WESAD** is stress physiology, not CKD. Domain familiarity was required to interpret metrics honestly and write §6.2 limitations.

**EP5 — Extent of applicable codes**  
Full regulatory codes (FDA SaMD, IEC 62304, HIPAA operational compliance) apply to **production** clinical systems—not fully implemented here. **PEP 8**, open dataset DUAs, and research reproducibility norms **are** followed. EP5 is therefore **partially** applicable and marked blank in Table 5.1.

**EP6 — Stakeholder involvement**  
Stakeholders include **supervisor (clinical/AI guidance)**, **examiners**, **future clinicians and hospital IT** (indirect), **dataset custodians** (PhysioNet, CDC), and **patients** (only via de-identified records). Requirements were elicited through FYDP supervision rather than live hospital user studies.

**EP7 — Interdependence**  
Subsystems are coupled:

- MIMIC **feature matrix → model → calibration → threshold → SHAP → Streamlit CDS**  
- NHANES and WESAD branches feed **fusion architecture (§14)** conceptually  
- Failure in lab sparsity or label definition affects both metrics and UI summaries  
Joint design and evaluation were required; the **reporting lock** ties primary model choice across notebook, figures, and UI.

---

### Mapping with Knowledge Profile

**Table 5.2: Mapping with Knowledge Profile**

| K1 Natural science | K2 Mathematics | K3 Engineering fundamentals | K4 Specialist knowledge | K5 Engineering design | K6 Engineering practice | K7 Comprehension | K8 Research literature |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**K1 — Natural science:** Renal physiology and CKD progression (eGFR, creatinine, BUN) inform feature selection and limitation writing.

**K2 — Mathematics:** Sigmoid calibration, cross-entropy/logistic loss, AUROC/AUPRC integrals, ECE binning, SHAP Shapley attributions, Gaussian fusion proxy in §14.

**K3 — Engineering fundamentals:** Modular pipeline design, separation of train/validation/test, versioned artifacts, failure handling for missing labs (imputation).

**K4 — Specialist knowledge:** MIMIC-IV schema (`hadm_id`, `subject_id`, `labevents`), NHANES survey weights and biochemistry, WESAD sensor modalities, grouped CV for leakage prevention.

**K5 — Engineering design:** Original **multimodal CKD framework** architecture—three branches + fusion protocol + CDS prototype—not a single off-the-shelf Kaggle script.

**K6 — Engineering practice:** Virtual environment (`.venv312`), staged notebook cells, exported CSV/PNG/pickle, `scripts/plot_*.py`, smoke-tested Streamlit, documented runbook (`UI_RUN.md`).

**K7 — Comprehension:** Results interpreted in clinical context—e.g., moderate MIMIC AUROC (~0.76) is meaningful with calibration; NHANES high AUROC is **not** pooled with MIMIC; sparse labs explain blank UI fields.

**K8 — Research literature:** Literature on MIMIC ML, calibration (Guo et al.), SHAP in healthcare, multimodal fusion, and CKD screening motivates Table 2.3 gaps and methodology choices.

---

### 5.4.2 Engineering Activities

**Table 5.3: Mapping with Complex Engineering Activities**

| EA1 Range of resources | EA2 Level of interaction | EA3 Innovation | EA4 Consequences for society/environment | EA5 Familiarity |
|:---:|:---:|:---:|:---:|:---:|
| ✓ | ✓ | ✓ | ✓ | ✓ |

**EA1 — Range of resources**  
Heterogeneous resources: **three public datasets**, credentialed hospital download, **multi-GB lab files**, Python ML stack, neural and classical models, figure pipeline, and Streamlit UI—coordinated under one output directory.

**EA2 — Level of interaction**  
- **Human–system:** Clinician-like user adjusts threshold, browses admissions, reads explanations in CDS.  
- **System–system:** Notebook exports checkpoints consumed by Streamlit; SHAP CSV drives global tab.  
- **Research–institution:** PhysioNet DUA governs MIMIC use.

**EA3 — Innovation**  
1. **Integrated multimodal CKD framework** with honest fusion boundary on disjoint data.  
2. **Leakage-aware + calibrated + explainable** MIMIC branch as primary evidence.  
3. **Frozen reproducible artifact chain** from notebook to thesis figures to CDS demo.

**EA4 — Consequences for society and environment**  
Potential to improve early CKD awareness and responsible AI reporting (calibration + XAI); low direct environmental impact; ethical risks mitigated by disclaimers and limitation section. Aligns with **SDG 3**.

**EA5 — Familiarity**  
Team acquired familiarity with CKD labeling conventions, MIMIC admission/lab semantics, wearable stress datasets, and clinical ML reporting norms through iterative supervisor meetings and literature review—beyond a standard classroom assignment.

---

## 5.5 Summary

This chapter showed that the project follows appropriate **software and research engineering practices**, addresses **ethical and societal context** for clinical ML, and meets **complex engineering problem** criteria through multidisciplinary depth, conflicting-requirement trade-offs, rigorous analysis, stakeholder awareness, and interdependent subsystems. **Engineering activity** criteria are met across resource breadth, interaction levels, innovation, societal relevance, and domain familiarity—within the honest scope of a **research FYDP**, not a deployed medical device.

---

## Word paste checklist

1. Insert **Tables 5.1, 5.2, 5.3** with checkmarks (✓) as shown.  
2. Keep **EP5** empty or footnote “partial—research prototype only.”  
3. Adjust **§5.3.1 weeks** to match your actual logbook.  
4. Add your **supervisor name** and **GPU model** in §5.1.2 if required by department.  
5. Cross-reference **Table 2.3** (gap analysis) and **§6.2** (limitations).

---

## Defence one-liner (Chapter 5)

> “Chapter 5 maps our CKD framework to complex engineering criteria: we balanced discrimination, calibration, and explainability on MIMIC, integrated three data modalities under resource constraints, and delivered a reproducible artifact chain—not a regulated clinical product.”
