## CKD FYDP `src` structure

Modular codebase for the thesis pipeline. **Canonical run path:** `notebooks/ckd_supervisor_pipeline_from_scratch.ipynb`.

See also: `docs/PROJECT_STRUCTURE.md`.

### Folder map

- `config/` — experiment paths and runtime settings
- `data/loaders/` — NHANES, MIMIC, WESAD loaders (`ckd_loaders.py`)
- `data/preprocess/` — cleaning and harmonization per source
- `data/labels/` — CKD label definitions and cohort builders
- `data/splits/` — leakage-safe grouped splits
- `models/` — tabular deep models, tree baselines, fusion stub
- `eval/` — metrics, calibration, uncertainty helpers
- `utils/` — seed, logging, run tracking

CLI wrappers live in `scripts/` (`load_ckd_datasets.py`, `scan_datasets.py`).
