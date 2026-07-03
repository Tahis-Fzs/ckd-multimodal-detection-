# Supervisor pipeline — output summary

**Objectives and motivation:** see [`../CANONICAL_OBJECTIVE_AND_MOTIVATION.md`](../CANONICAL_OBJECTIVE_AND_MOTIVATION.md).

## Dataset paths (resolved at runtime)

Primary shared folder: **`/Users/md.shadmantahsin/Desktop/STUDY/Dataset/`**

| Branch | Resolved path |
|--------|----------------|
| MIMIC-IV hosp | `STUDY/Dataset/mimic-iv-3.1/hosp/` |
| NHANES CSV | `STUDY/Dataset/nhanes_ckd/csv/` |
| WESAD | `STUDY/Dataset/WESAD/` |

Notebook helpers: `resolve_mimic_hosp()`, `resolve_nhanes_csv_root()`, `resolve_wesad_root()` in `## 0) Setup`.

## Output directory

**`CKD Dataset/outputs/supervisor_runs/`** (`OUT = ROOT / "outputs" / "supervisor_runs"`)

## Artifact files

| File | Description |
|------|-------------|
| `from_scratch_clinical_nhanes.json` | NHANES run metadata + metrics |
| `from_scratch_clinical_nhanes_summary.csv` | NHANES compact table |
| `step2_mimic_admission_branch.json` | MIMIC Step 2 run (FAST_DEV=False final) |
| `step2_mimic_admission_summary.csv` | MIMIC compact table |
| `step2_mimic_admission_summary_extended.csv` | MIMIC + RF/XGB baselines |
| `step2_mimic_checkpoint.pkl` | Step2 resume checkpoint |
| `step2_mimic_operating_point_summary.csv` | 12C threshold policies |
| `step2_mimic_robustness_per_seed.csv` | 12D per-seed metrics |
| `step2_mimic_robustness_mean_std.csv` | 12D mean±std |
| `step2_mimic_calibration_summary.csv` | 12E calibration comparison |
| `step2_mimic_permutation_importance_top15.csv` | 15 XAI top features |
| `step3_fusion_spec.csv` | Branch champions + weights |
| `step3_fusion_protocol.json` | Late-fusion protocol |
| `step3_fusion_demo_summary.csv` | 14D proxy demo (2-branch, not final eval) |
| `step3_fusion_final_stub_summary.csv` | 14D-final 3-branch proxy stub |
| `step3_fusion_spec_3branch.csv` | NHANES+MIMIC+wearable fusion weights |
| `wearable_branch_summary.json` | WESAD demo baseline metrics |
| `wearable_branch_probs_demo.csv` | Window-level wearable probabilities |
| `fusion_final_evaluation_status.json` | Fusion status (wearable integrated; alignment pending) |
| `final_reporting_lock.json` | Reporting model/threshold lock |
| `wearable_branch_status.json` | WESAD integration status (`integrated: true` after §16) |
| `supervisor_progress_model_pack.csv` | Combined progress pack |
| `supervisor_progress_status.json` | Progress snapshot |

## Fusion status

- **Setup complete:** 14A–14C protocol and weights saved.
- **Wearable branch:** §16 trains demo WESAD baseline (stress vs baseline proxy); exports `wearable_branch_*` artifacts.
- **Demo only:** 14D (2-branch) and 14D-final (3-branch) use branch-level proxy centers — not aligned patient fusion.
- **Final eval pending:** shared validation design with aligned NHANES+MIMIC+wearable probabilities (see `fusion_final_evaluation_status.json`).

## Regeneration

Re-run notebook cells in supervisor-safe order; files are overwritten on save.
