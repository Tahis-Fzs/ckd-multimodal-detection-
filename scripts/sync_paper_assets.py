#!/usr/bin/env python3
"""Copy thesis figures/tables from outputs/supervisor_runs → paper_assets/."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "supervisor_runs"
FIG = ROOT / "paper_assets" / "figures"
TAB = ROOT / "paper_assets" / "tables"
RES = ROOT / "Results" / "figures"

FIG_PATTERNS = (
    "fig_mimic_*.png",
    "fig_ui_*.png",
    "figure_3_6_wesad_window.png",
)
TABLE_FILES = (
    "final_reporting_lock.json",
    "step2_mimic_calibration_summary.csv",
    "step2_mimic_shap_top15.csv",
    "step2_mimic_confusion_matrix_logreg_sigmoid_cal.csv",
    "from_scratch_clinical_nhanes_summary.csv",
    "wearable_branch_summary.json",
    "fusion_meta_comparison.csv",
)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    n = 0
    for pat in FIG_PATTERNS:
        for src in OUT.glob(pat):
            shutil.copy2(src, FIG / src.name)
            print(f"figure: {src.name}")
            n += 1
    wesad = RES / "figure_3_6_wesad_window.png"
    if wesad.is_file():
        shutil.copy2(wesad, FIG / wesad.name)
        print(f"figure: {wesad.name}")
        n += 1
    for name in TABLE_FILES:
        src = OUT / name
        if src.is_file():
            shutil.copy2(src, TAB / name)
            print(f"table: {name}")
            n += 1
    print(f"Synced {n} assets to paper_assets/")


if __name__ == "__main__":
    main()
