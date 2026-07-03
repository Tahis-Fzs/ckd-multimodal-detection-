# External validation — MIMIC CKD pipeline

## What you ran

| Cell | Purpose | Validation type |
|------|---------|-----------------|
| **12D** | Repeated **random grouped** splits (by `subject_id`) | **Internal** — different subject groups, same admission time distribution |
| **12G** | **Temporal external** split (train earlier subjects, test later subjects) | **External (temporal)** — simulates deployment on future admissions |

Run order for temporal validation only: **`12B-Resume` → `12G`** (after Setup / kernel check).

## Internal vs external

**Internal validation** keeps the same cohort and resplits subjects at random while preserving group integrity (no subject appears in both train and test). Metrics reflect stability across splits but not temporal drift.

**External (temporal) validation** assigns each **subject** to train or test from their **first** `admittime`:

- Subjects whose first admission is **before** the 80th-percentile cutoff → **train** (all their admissions).
- Subjects whose first admission is **on or after** the cutoff → **test** (all their admissions).

Preprocessing, imputation, scaling, model fitting, and calibration are fit **only on the temporal train set**, then evaluated on the held-out future test set. This avoids leakage across time and across multiple admissions per patient.

**True external validation** across databases (e.g. train MIMIC, test eICU) is **Phase 2** and is **not implemented** in this notebook.

## Outputs

- `outputs/supervisor_runs/step2_mimic_temporal_external_summary.csv`
- `outputs/supervisor_runs/step2_mimic_temporal_external.json`

## Defence one-liner

> We report random grouped splits (12D) for split stability and a subject-level temporal holdout (12G) where models trained on earlier admissions are evaluated on later ones; cross-database external validation on eICU is planned as Phase 2.
