# Notebook kernel (stable Python 3.12)

Python **3.14** in `.venv` can segfault in VS Code/Jupyter on macOS. Use **`.venv312`** instead.

## In VS Code / Cursor

1. Open `ckd_supervisor_pipeline_from_scratch.ipynb`
2. **Kernel → Select Kernel**  
   - If **Jupyter Kernel** list is blank: use **`Python Environments...`** →  
     `CKD Dataset/.venv312/bin/python` (Python 3.12.6)  
   - Or **Jupyter Kernel** → **`CKD Python 3.12`** / **`Python (CKD Dataset 3.12)`**  
   (Do **not** use **3.14** or `.venv` without `312`.)
3. **Kernel → Restart Kernel**
4. Run cells under **SUPERVISOR RUN ORDER** — one at a time

## Verify (terminal)

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
.venv312/bin/python -c "import torch, sklearn, xgboost; print('OK')"
```

## Recreate venv (if needed)

```bash
cd "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 -m venv .venv312
.venv312/bin/pip install -r requirements.txt ipykernel
.venv312/bin/python -m ipykernel install --user --name ckd-312 --display-name "CKD Python 3.12"
```
