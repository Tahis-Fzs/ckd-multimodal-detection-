"""
Plot confusion matrix for primary MIMIC model (logreg_sigmoid_cal) on held-out test set.

Usage (from CKD Dataset):
  .venv312/bin/python scripts/plot_mimic_confusion_matrix.py
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

try:
    from sklearn.frozen import FrozenEstimator
except ImportError:
    from sklearn.base import BaseEstimator

    class FrozenEstimator(BaseEstimator):
        def __init__(self, estimator):
            self.estimator = estimator

        def fit(self, X, y=None):
            return self

        def predict_proba(self, X):
            return self.estimator.predict_proba(X)

        def predict(self, X):
            return self.estimator.predict(X)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "supervisor_runs"
CHECKPOINT = OUT / "step2_mimic_checkpoint.pkl"
CALIBRATION_CSV = OUT / "step2_mimic_calibration_summary.csv"
MODEL_NAME = "logreg_sigmoid_cal"


def main() -> None:
    if not CHECKPOINT.is_file():
        raise FileNotFoundError(f"Run notebook 12B first: {CHECKPOINT}")

    with open(CHECKPOINT, "rb") as f:
        ckpt = pickle.load(f)

    base2 = ckpt["base2"]
    X2_va = ckpt["X2_va"]
    y2_va = ckpt["y2_va"]
    X2_te = ckpt["X2_te"]
    y2_te = np.asarray(ckpt["y2_te"])

    cal = CalibratedClassifierCV(FrozenEstimator(base2), method="sigmoid")
    cal.fit(X2_va, y2_va)
    p_te = cal.predict_proba(X2_te)[:, 1]

    threshold = 0.16
    if CALIBRATION_CSV.is_file():
        row = pd.read_csv(CALIBRATION_CSV)
        hit = row.loc[row["model"] == MODEL_NAME]
        if len(hit):
            threshold = float(hit.iloc[0]["threshold"])

    y_pred = (p_te >= threshold).astype(int)
    cm = confusion_matrix(y2_te, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    summary = pd.DataFrame(
        [
            {
                "model": MODEL_NAME,
                "split": "test",
                "threshold": threshold,
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
                "n": int(len(y2_te)),
                "prevalence": float(y2_te.mean()),
            }
        ]
    )
    csv_path = OUT / "step2_mimic_confusion_matrix_logreg_sigmoid_cal.csv"
    summary.to_csv(csv_path, index=False)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["CKD proxy negative", "CKD proxy positive"],
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title(
        f"MIMIC test set — {MODEL_NAME}\n(threshold = {threshold:.2f}, n = {len(y2_te):,})"
    )
    fig.tight_layout()
    png_path = OUT / "fig_mimic_confusion_matrix_logreg_sigmoid_cal.png"
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    meta = {
        "model": MODEL_NAME,
        "split": "test",
        "threshold": threshold,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "figure": png_path.name,
        "csv": csv_path.name,
    }
    with open(OUT / "step2_mimic_confusion_matrix_logreg_sigmoid_cal.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved: {png_path}")
    print(f"Saved: {csv_path}")
    print(f"TN={tn} FP={fp} FN={fn} TP={tp}")


if __name__ == "__main__":
    main()
