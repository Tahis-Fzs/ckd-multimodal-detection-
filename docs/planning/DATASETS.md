# Where the datasets live

All multimodal data for the CKD FYDP is organized under:

`**[CKD Dataset/](CKD%20Dataset/README.md)**`

- **NHANES** → `[CKD Dataset/nhanes_ckd/](CKD%20Dataset/nhanes_ckd/README.md)` (CSVs + scripts)
- **WESAD** → `[CKD Dataset/WESAD/](CKD%20Dataset/WESAD)` (per-subject `.pkl`)
- **MIMIC-IV** → `[CKD Dataset/mimic-iv-3.1/](CKD%20Dataset/mimic-iv-3.1)` (unpack `hosp/` + `icu/` here)
- **MIMIC-IV-ED** → `[CKD Dataset/mimic-iv-ed-2.2/](CKD%20Dataset/mimic-iv-ed-2.2)` (ED tables under `ed/`)
- **MIMIC-IV-ECG** → `[CKD Dataset/mimic-iv-ecg/](CKD%20Dataset/mimic-iv-ecg)` (12-lead WFDB waveforms; pair with MIMIC-IV per PhysioNet docs)

**Snapshot:** [`data/DATASET_INVENTORY.md`](../../data/DATASET_INVENTORY.md)