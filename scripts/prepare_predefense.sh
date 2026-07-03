#!/usr/bin/env bash
# One-shot pre-defense prep: figures, tables, inventory, summary CSV, smoke checks.
# Usage: cd "CKD Dataset" && ./scripts/prepare_predefense.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export MPLCONFIGDIR="${MPLCONFIGDIR:-$ROOT/.mplconfig}"
export MPLBACKEND="${MPLBACKEND:-Agg}"

WESAD_ROOT="${WESAD_ROOT:-/Users/md.shadmantahsin/Desktop/STUDY/Dataset/WESAD}"
PY="${PY:-$ROOT/.venv312/bin/python}"

echo "== CKD pre-defense prepare =="
echo "ROOT=$ROOT"

if [[ ! -x "$PY" ]]; then
  echo "ERROR: missing $PY — create .venv312 first." >&2
  exit 1
fi

echo "-- 1/6 MIMIC thesis figures --"
"$PY" scripts/plot_mimic_thesis_figures.py
"$PY" scripts/plot_mimic_confusion_matrix.py

echo "-- 2/6 WESAD figure 3.6 --"
if [[ -d "$WESAD_ROOT" ]]; then
  "$PY" Results/figures/make_figure_3_6_wesad_window.py \
    --wesad_root "$WESAD_ROOT" \
    --subject S2 \
    --window_samples 1920 \
    --window_index 0 \
    --out "Results/figures/figure_3_6_wesad_window.png"
else
  echo "WARN: WESAD not found at $WESAD_ROOT — skip figure 3.6"
fi

echo "-- 3/6 Sync paper_assets --"
"$PY" scripts/sync_paper_assets.py

echo "-- 4/6 Dataset inventory --"
"$PY" scripts/scan_datasets.py

echo "-- 5/6 Export pre-defense summary tables --"
"$PY" scripts/export_predefense_summary.py

echo "-- 6/6 Smoke checks --"
"$PY" - <<'PY'
from pathlib import Path
import pickle

root = Path(".")
out = root / "outputs/supervisor_runs"
need = [
    out / "final_reporting_lock.json",
    out / "step2_mimic_checkpoint.pkl",
    out / "step2_mimic_calibration_summary.csv",
    root / "paper_assets/figures/fig_mimic_model_auroc.png",
]
missing = [str(p) for p in need if not p.is_file()]
if missing:
    raise SystemExit("Missing: " + ", ".join(missing))
with open(out / "step2_mimic_checkpoint.pkl", "rb") as f:
    ckpt = pickle.load(f)
assert "base2" in ckpt, "checkpoint missing base2"
print("Smoke OK — checkpoint + lock + figures present")
PY

echo ""
echo "DONE. Next steps:"
echo "  1. Paste docs/thesis/*.md into Word"
echo "  2. Insert paper_assets/figures/*.png"
echo "  3. Slides: docs/PRE_DEFENSE_SLIDES.md"
echo "  4. Demo: ./run_cds_app.sh"
echo "  5. Zip (optional): ./scripts/build_fydp_zip.sh"
