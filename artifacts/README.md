# Artifacts

Frozen checkpoints, metrics JSON/CSV, and thesis figures are written to:

`outputs/supervisor_runs/`

Key files:

| File | Purpose |
|------|---------|
| `final_reporting_lock.json` | Locked primary model and threshold policy |
| `step2_mimic_checkpoint.pkl` | MIMIC Step 2 resume checkpoint |
| `step2_mimic_calibration_summary.csv` | Calibration comparison table |
| `step2_mimic_shap_top15.csv` | Global SHAP ranking |

Copies for Word/slides: `paper_assets/figures/` and `paper_assets/tables/`.

Large files are gitignored; include the checkpoint in your submission zip or document re-run steps in `docs/SUBMISSION.md`.
