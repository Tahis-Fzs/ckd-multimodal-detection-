"""
Generate MIMIC thesis figures (Viz-1..3) from frozen checkpoint / CSV artifacts.

Usage (from CKD Dataset):
  MPLCONFIGDIR="$(pwd)/.mplconfig" MPLBACKEND=Agg .venv312/bin/python scripts/plot_mimic_thesis_figures.py
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

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
EXT_CSV = OUT / "step2_mimic_admission_summary_extended.csv"
SHAP_CSV = OUT / "step2_mimic_shap_top15.csv"


def plot_calibration_reliability() -> Path:
    with open(CHECKPOINT, "rb") as f:
        ckpt = pickle.load(f)

    base2 = ckpt["base2"]
    X2_va = ckpt["X2_va"]
    y2_va = ckpt["y2_va"]
    X2_te = ckpt["X2_te"]
    y2_te = np.asarray(ckpt["y2_te"])

    cal = CalibratedClassifierCV(FrozenEstimator(base2), method="sigmoid")
    cal.fit(X2_va, y2_va)

    p_uncal = base2.predict_proba(X2_te)[:, 1]
    p_cal = cal.predict_proba(X2_te)[:, 1]

    fig, ax = plt.subplots(figsize=(6, 5))
    for label, p, color in [
        ("Uncalibrated LogReg", p_uncal, "#d62728"),
        ("Sigmoid calibrated", p_cal, "#2ca02c"),
    ]:
        frac_pos, mean_pred = calibration_curve(y2_te, p, n_bins=10, strategy="quantile")
        ax.plot(mean_pred, frac_pos, "o-", label=label, color=color, linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration", alpha=0.6)
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_title("MIMIC test — calibration reliability")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = OUT / "fig_mimic_calibration_reliability.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_model_auroc_bars() -> Path:
    df = pd.read_csv(EXT_CSV).sort_values("auroc", ascending=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(df["model"], df["auroc"], color="#1f77b4")
    ax.set_xlim(0.72, 0.80)
    ax.set_xlabel("Test AUROC")
    ax.set_title("MIMIC admission branch — model comparison")
    for _, r in df.iterrows():
        ax.text(r["auroc"] + 0.001, r["model"], f"{r['auroc']:.3f}", va="center", fontsize=9)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()

    out = OUT / "fig_mimic_model_auroc.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_shap_top10() -> Path:
    df = pd.read_csv(SHAP_CSV).head(10).sort_values("mean_abs_shap", ascending=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(df["feature"], df["mean_abs_shap"], color="#9467bd")
    ax.set_xlabel("Mean |SHAP|")
    ax.set_title("MIMIC logreg_sigmoid_cal — top 10 features (SHAP)")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()

    out = OUT / "fig_mimic_shap_top10.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    if not CHECKPOINT.is_file():
        raise FileNotFoundError(f"Run notebook 12B first: {CHECKPOINT}")
    if not EXT_CSV.is_file():
        raise FileNotFoundError(f"Run notebook 12F first: {EXT_CSV}")
    if not SHAP_CSV.is_file():
        raise FileNotFoundError(f"Run notebook 15B first: {SHAP_CSV}")

    paths = [
        plot_calibration_reliability(),
        plot_model_auroc_bars(),
        plot_shap_top10(),
    ]
    for p in paths:
        print(f"Saved: {p}")


if __name__ == "__main__":
    main()
