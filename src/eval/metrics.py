from __future__ import annotations

from typing import Dict

import numpy as np
import warnings


def safe_auroc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    try:
        from sklearn.metrics import roc_auc_score
    except ImportError as e:
        raise ImportError("scikit-learn is required for AUROC.") from e
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return float(roc_auc_score(y_true, y_prob))
    except ValueError:
        return float("nan")


def safe_auprc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    try:
        from sklearn.metrics import average_precision_score
    except ImportError as e:
        raise ImportError("scikit-learn is required for AUPRC.") from e
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return float(average_precision_score(y_true, y_prob))
    except ValueError:
        return float("nan")


def binary_metrics_at_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    threshold: float = 0.5,
) -> Dict[str, float]:
    """
    Compute clinically useful binary metrics at a fixed decision threshold.
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    y_pred = (y_prob >= threshold).astype(int)

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))

    sens = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    spec = tn / (tn + fp) if (tn + fp) > 0 else float("nan")
    ppv = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    npv = tn / (tn + fn) if (tn + fn) > 0 else float("nan")
    f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else float("nan")
    acc = (tp + tn) / len(y_true) if len(y_true) > 0 else float("nan")
    bal_acc = np.nanmean([sens, spec])

    return {
        "threshold": float(threshold),
        "accuracy": float(acc),
        "balanced_accuracy": float(bal_acc),
        "sensitivity_recall": float(sens),
        "specificity": float(spec),
        "precision_ppv": float(ppv),
        "npv": float(npv),
        "f1": float(f1),
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
    }


__all__ = [
    "safe_auroc",
    "safe_auprc",
    "binary_metrics_at_threshold",
]
