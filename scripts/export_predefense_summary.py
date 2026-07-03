#!/usr/bin/env python3
"""Export one-page pre-defense metrics summary for Word/report paste."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "supervisor_runs"
PAPER = ROOT / "paper_assets" / "tables"
PAPER.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rows = []

    lock = json.loads((OUT / "final_reporting_lock.json").read_text())
    cal = pd.read_csv(OUT / "step2_mimic_calibration_summary.csv")
    primary = cal[cal["model"] == lock["mimic_model"]].iloc[0]
    rows.append(
        {
            "branch": "MIMIC (primary)",
            "model": lock["mimic_model"],
            "threshold": primary["threshold"],
            "accuracy": primary["accuracy"],
            "f1": primary["f1"],
            "auroc": primary["auroc"],
            "ece": primary["ece"],
            "note": "Locked primary — hospital admission CKD proxy",
        }
    )

    nhanes = pd.read_csv(OUT / "from_scratch_clinical_nhanes_summary.csv")
    best_nh = nhanes.sort_values("auroc", ascending=False).iloc[0]
    rows.append(
        {
            "branch": "NHANES",
            "model": best_nh["model"],
            "threshold": "",
            "accuracy": best_nh["accuracy"],
            "f1": best_nh["f1"],
            "auroc": best_nh["auroc"],
            "ece": best_nh["ece"],
            "note": "Separate population cohort — not primary hospital evidence",
        }
    )

    wear = json.loads((OUT / "wearable_branch_summary.json").read_text())
    m = wear["metrics_holdout_group_split"]
    rows.append(
        {
            "branch": "WESAD (wearable proxy)",
            "model": wear["model"],
            "threshold": "",
            "accuracy": m["accuracy"],
            "f1": m["f1"],
            "auroc": m["auroc"],
            "ece": m["ece"],
            "note": "Stress vs baseline — NOT CKD labeled",
        }
    )

    fusion = pd.read_csv(OUT / "fusion_meta_comparison.csv")
    for _, r in fusion.iterrows():
        rows.append(
            {
                "branch": "Fusion (proxy holdout)",
                "model": r["fusion_method"],
                "threshold": r["threshold"],
                "accuracy": r["accuracy"],
                "f1": r["f1"],
                "auroc": r["auroc"],
                "ece": r["ece"],
                "note": "No same-patient aligned multimodal cohort",
            }
        )

    df = pd.DataFrame(rows)
    path = PAPER / "predefense_metrics_summary.csv"
    df.to_csv(path, index=False)
    print(f"Saved: {path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
