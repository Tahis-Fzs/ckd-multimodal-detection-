# Pre-defense checklist (DIU FYDP)

**Student:** Md. Shadman Tahsin  
**Supervisor:** Dr. Naznin Sultana  
**Target:** Pre-defense / title defense presentation

---

## Done in repo (verified)

- [x] NHANES branch artifacts (`from_scratch_clinical_nhanes.json`, summaries)
- [x] MIMIC primary lock (`logreg_sigmoid_cal`, threshold 0.16)
- [x] MIMIC checkpoint (~24 MB): `outputs/supervisor_runs/step2_mimic_checkpoint.pkl`
- [x] Calibration, SHAP, temporal, robustness JSON/CSV
- [x] WESAD wearable branch + probs export
- [x] Fusion protocol + meta comparison (proxy holdout)
- [x] CDS app: `app/demo_app.py`
- [x] Thesis figure refresh (run date: regenerate via scripts below)
- [x] `paper_assets/figures/` synced from outputs
- [x] Chapter drafts: Ch1–Ch3, Ch4, Ch5, Ch6, §6.2 in `docs/thesis/`
- [x] One-shot prep script: `scripts/prepare_predefense.sh`
- [x] Slides outline: `docs/PRE_DEFENSE_SLIDES.md`
- [x] FYDP zip builder: `scripts/build_fydp_zip.sh`
- [x] Dataset inventory: `data/DATASET_INVENTORY.md`

---

## Your tasks before pre-defense (Word / PMS)

- [ ] Open **`docs/thesis/FYDP_REPORT_Summer2025.docx`** (full Summer 2025 template report)
- [ ] Fill placeholders: student ID, dates, board of examiners, signatures
- [ ] Insert figures from `paper_assets/figures/`; generate Word TOC
- [ ] Or edit chapter drafts individually: `docs/thesis/THESIS_CH*.md`
- [ ] Insert figures from `paper_assets/figures/`:
  - `fig_mimic_calibration_reliability.png`
  - `fig_mimic_model_auroc.png`
  - `fig_mimic_shap_top10.png`
  - `fig_mimic_confusion_matrix_logreg_sigmoid_cal.png`
  - `figure_3_6_wesad_window.png`
  - `fig_ui_*.png` (CDS demo)
- [ ] Prepare 10–15 slide deck from `docs/PRE_DEFENSE_SLIDES.md`
- [ ] Practice honest lines: ML-primary, WESAD proxy, no patient-level merge

---

## Regenerate assets (one command)

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
chmod +x scripts/prepare_predefense.sh scripts/build_fydp_zip.sh
./scripts/prepare_predefense.sh
```

Optional submission zip:

```bash
./scripts/build_fydp_zip.sh
```

---

## Run CDS demo live

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
./run_cds_app.sh
```

Default demo admission: index **148**, `hadm_id=24251211`.

---

## Key numbers to memorize (primary MIMIC)

| Item | Value |
|------|-------|
| Model | logreg_sigmoid_cal |
| Threshold | 0.16 |
| Test AUROC | 0.7614 |
| ECE | 0.0203 |
| Admissions | ~30,000 |
| Features | 68 |

---

## Honest limitation lines (examiner)

1. NHANES, MIMIC, WESAD — **no same-patient ID**; fusion is protocol/proxy.
2. WESAD — **stress proxy**, not CKD labels.
3. Primary model — **calibrated logistic regression**, not end-to-end deep learning on raw signals.
4. CDS UI — **research prototype**, not clinical deployment.

---

## Submission zip (final, not necessarily pre-defense)

See `docs/SUBMISSION.md`. Include checkpoint or re-run note; exclude raw `STUDY/Dataset/`.
