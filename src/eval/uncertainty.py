from __future__ import annotations

from typing import Callable, Tuple

import numpy as np
import warnings


def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    metric_fn: Callable[[np.ndarray, np.ndarray], float],
    *,
    n_boot: int = 300,
    alpha: float = 0.95,
    random_state: int = 42,
) -> Tuple[float, float, float]:
    """
    Bootstrap CI for probabilistic metrics.
    Returns (mean, lower, upper).
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    n = len(y_true)
    if n == 0:
        return float("nan"), float("nan"), float("nan")

    rng = np.random.default_rng(random_state)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                v = float(metric_fn(y_true[idx], y_prob[idx]))
        except Exception:
            continue
        if not np.isnan(v):
            vals.append(v)

    if not vals:
        return float("nan"), float("nan"), float("nan")

    arr = np.array(vals, dtype=float)
    lo = float(np.quantile(arr, (1.0 - alpha) / 2.0))
    hi = float(np.quantile(arr, 1.0 - (1.0 - alpha) / 2.0))
    return float(np.mean(arr)), lo, hi


__all__ = ["bootstrap_metric_ci"]
