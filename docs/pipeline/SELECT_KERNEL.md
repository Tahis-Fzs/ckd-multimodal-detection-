# Fix blank "Select a Jupyter Kernel" in Cursor

**Do not use "Jupyter Kernel..."** if the list is empty.

## Method A (recommended): Enter interpreter path

1. Top-right **Select Kernel**
2. **Python Environments...**
3. **Enter interpreter path...** (or "Enter path to Python interpreter")
4. Paste exactly:

```
/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset/.venv312/bin/python
```

5. **Restart kernel**
6. Run first notebook cell → must show `3.12.6` and `.venv312`

## Method B: Command Palette

1. `Cmd + Shift + P`
2. **Python: Select Interpreter**
3. **Enter interpreter path...**
4. Paste the same path as above
5. Reopen notebook → kernel should connect

## Method C: Reload then pick

1. `Cmd + Shift + P` → **Developer: Reload Window**
2. **Select Kernel** → should show **Python 3.12.6 ('.venv312': venv)**
3. If not, use Method A

## Verify in terminal

```bash
"/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset/.venv312/bin/python" -c "import sys; print(sys.version)"
```

Expected: `3.12.6`
