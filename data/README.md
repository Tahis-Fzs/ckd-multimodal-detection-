# Data (external — not in Git)

Large cohort files live **outside** this repository, same pattern as research repos that exclude raw CT/MIMIC data from GitHub.

## Canonical location

```
/Users/md.shadmantahsin/Desktop/STUDY/Dataset/
├── mimic-iv-3.1/hosp/
├── nhanes_ckd/csv/
└── WESAD/
```

## Symlinks in this project

| Path | Points to |
|------|-----------|
| `Title Defence/Dataset` | `STUDY/Dataset` |
| `CKD Dataset/data/datasets` | `Title Defence/Dataset` |

The supervisor notebook resolves these automatically (`resolve_mimic_hosp`, etc.).

## Do not move multi-GB data into `CKD Dataset/`

- Keeps submission zip small  
- Avoids duplicating MIMIC on disk  
- Matches PhysioNet use (credentialed download on each machine)

For submission, include **`data/DATASET_INVENTORY.md`** + this README, not the raw `.gz` files.
