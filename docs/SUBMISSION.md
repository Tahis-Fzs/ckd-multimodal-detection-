# Submission checklist (DIU CSE FYDP)

## Include in zip / CD (code folder)

- [ ] `README.md`, `requirements.txt`, `.gitignore`
- [ ] `notebooks/ckd_supervisor_pipeline_from_scratch.ipynb`
- [ ] `app/`, `src/`, `scripts/`
- [ ] `paper_assets/figures/` and `paper_assets/tables/`
- [ ] `docs/thesis/` drafts (optional)
- [ ] `data/README.md` + `data/DATASET_INVENTORY.md`
- [ ] `outputs/supervisor_runs/step2_mimic_checkpoint.pkl` **or** note to re-run cell 12B
- [ ] `outputs/README.md`

## Exclude

- [ ] `.venv312/`, `__pycache__/`, `.mplconfig/`
- [ ] Raw MIMIC / NHANES / WESAD (`STUDY/Dataset/`)
- [ ] `archive/legacy/.venv*`

## Report (separate PDF)

- Research TOC template · Turnitin ≤25% · PMS upload

## Build zip (example)

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence"
find "CKD Dataset" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
zip -r CKD_FYDP_code.zip "CKD Dataset" \
  -x "CKD Dataset/.venv*" "CKD Dataset/**/__pycache__/*" \
  -x "CKD Dataset/outputs/supervisor_runs/*"
# Then manually add checkpoint + paper_assets if needed
```
