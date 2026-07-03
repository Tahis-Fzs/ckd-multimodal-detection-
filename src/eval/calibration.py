from __future__ import annotations

from typing import Tuple

import numpy as np


def brier_score_binary(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype(float)
    y_prob = np.asarray(y_prob).astype(float)
    if len(y_true) == 0:
        return float("nan")
    return float(np.mean((y_prob - y_true) ** 2))


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    n_bins: int = 10,
) -> float:
    """
    Simple ECE with equal-width bins in [0, 1].
    """
    y_true = np.asarray(y_true).astype(float)
    y_prob = np.asarray(y_prob).astype(float)
    if len(y_true) == 0:
        return float("nan")

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        left, right = bins[i], bins[i + 1]
        # include right edge only in last bin
        if i < n_bins - 1:
            idx = (y_prob >= left) & (y_prob < right)
        else:
            idx = (y_prob >= left) & (y_prob <= right)
        if not np.any(idx):
            continue
        conf = float(np.mean(y_prob[idx]))
        acc = float(np.mean(y_true[idx]))
        weight = float(np.mean(idx))
        ece += weight * abs(acc - conf)
    return float(ece)


def select_threshold_by_youden(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    steps: int = 201,
) -> Tuple[float, float]:
    """
    Pick threshold maximizing Youden's J = sensitivity + specificity - 1 on validation data.
    Returns (best_threshold, best_j).
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    thresholds = np.linspace(0.0, 1.0, steps)
    best_t = 0.5
    best_j = float("-inf")
    for t in thresholds:
        pred = (y_prob >= t).astype(int)
        tp = np.sum((pred == 1) & (y_true == 1))
        tn = np.sum((pred == 0) & (y_true == 0))
        fp = np.sum((pred == 1) & (y_true == 0))
        fn = np.sum((pred == 0) & (y_true == 1))
        sens = tp / (tp + fn) if (tp + fn) > 0 else np.nan
        spec = tn / (tn + fp) if (tn + fp) > 0 else np.nan
        j = sens + spec - 1 if not (np.isnan(sens) or np.isnan(spec)) else np.nan
        if not np.isnan(j) and j > best_j:
            best_j = float(j)
            best_t = float(t)
    return best_t, best_j


__all__ = [
    "brier_score_binary",
    "expected_calibration_error",
    "select_threshold_by_youden",
]
