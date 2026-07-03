# CKD FYDP — project structure

Phase **A** reorganisation complete. Training logic remains in the supervisor notebook.

## Layout

```text
CKD Dataset/
├── notebooks/ckd_supervisor_pipeline_from_scratch.ipynb
├── app/demo_app.py
├── src/          ← loaders, splits, eval, models
├── scripts/      ← load_ckd_datasets, scan_datasets, thesis figures
├── data/         ← README + DATASET_INVENTORY + datasets symlink
├── outputs/supervisor_runs/
├── paper_assets/
└── docs/
```

Legacy material: `Title Defence/archive/ckd_dataset/` (old notebooks, venv, `ckd_pipeline.py`).

## What did **not** change (on purpose)

- `outputs/supervisor_runs/` remains the notebook write target
- Dataset files stay in `STUDY/Dataset/` (symlinked via `data/datasets`)
- No `src/federated/` (not in thesis scope)

## Phase B (optional, post-defence)

- `src/inference/mimic_bundle.py` shared by app + scripts
- `configs/mimic_primary.yaml`
- Gradual migration from notebook cells → `src/training/`
