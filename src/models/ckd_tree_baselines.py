"""
Tree baselines (Random Forest, XGBoost) for tabular CKD pipelines.

Use the same train/val/test matrices as logistic regression / MLP (median-imputed,
standardized, train-only fit). Thresholds are chosen on validation via Youden's J
(sensitivity + specificity - 1), matching the supervisor notebook convention.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from src.eval.calibration import brier_score_binary, expected_calibration_error
from src.eval.metrics import binary_metrics_at_threshold, safe_auprc, safe_auroc


def best_youden_threshold(
    y_true: np.ndarray,
    p_prob: np.ndarray,
    thr_grid: np.ndarray,
) -> Tuple[float, float]:
    best_thr, best_j = 0.5, -1.0
    for t in thr_grid:
        m = binary_metrics_at_threshold(y_true, p_prob, threshold=float(t))
        j = m["sensitivity_recall"] + m["specificity"] - 1.0
        if j > best_j:
            best_thr, best_j = float(t), float(j)
    return best_thr, float(best_j)


def _metrics_pack(
    y_true: np.ndarray,
    p_prob: np.ndarray,
    *,
    threshold: float,
) -> Dict[str, Any]:
    pack = binary_metrics_at_threshold(y_true, p_prob, threshold=float(threshold))
    pack["auroc"] = float(safe_auroc(y_true, p_prob))
    pack["auprc"] = float(safe_auprc(y_true, p_prob))
    pack["ece"] = float(expected_calibration_error(y_true, p_prob))
    pack["brier"] = float(brier_score_binary(y_true, p_prob))
    return pack


def _eval_sklearn_prob_classifier(
    clf: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    thr_grid: np.ndarray,
) -> Dict[str, Any]:
    clf.fit(X_train, y_train)
    p_val = clf.predict_proba(X_val)[:, 1]
    p_test = clf.predict_proba(X_test)[:, 1]
    thr, _ = best_youden_threshold(y_val, p_val, thr_grid)
    val = _metrics_pack(y_val, p_val, threshold=thr)
    test = _metrics_pack(y_test, p_test, threshold=thr)
    return {"val": val, "test": test, "threshold": thr, "p_val": p_val, "p_test": p_test}


def _default_n_jobs() -> int:
    # macOS + Jupyter: n_jobs=-1 can hard-crash the kernel (OpenMP/fork).
    return 1 if sys.platform == "darwin" else -1


def fit_rf_xgb_tabular(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    *,
    thr_grid: Optional[np.ndarray] = None,
    random_state: int = 42,
    include_xgboost: bool = True,
    n_jobs: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fit RF (+ optional XGBoost) and return val/test metric dicts with Youden threshold on val.

    Parameters
    ----------
    thr_grid :
        Threshold search grid on validation probabilities. Default matches the
        supervisor notebook (0.1 .. 0.9, 161 points).
    """
    if thr_grid is None:
        thr_grid = np.linspace(0.1, 0.9, 161)
    if n_jobs is None:
        n_jobs = _default_n_jobs()

    y_train = np.asarray(y_train).astype(int)
    pos = int(np.sum(y_train == 1))
    neg = int(np.sum(y_train == 0))
    spw = float(neg / max(pos, 1))

    rf = RandomForestClassifier(
        n_estimators=400,
        max_depth=16,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=random_state,
        n_jobs=n_jobs,
    )
    out: Dict[str, Any] = {
        "random_forest": _eval_sklearn_prob_classifier(
            rf, X_train, y_train, X_val, y_val, X_test, y_test, thr_grid
        ),
        "xgboost": None,
        "xgboost_note": None,
    }

    if not include_xgboost:
        out["xgboost_note"] = "skipped (include_xgboost=False)"
        return out

    try:
        from xgboost import XGBClassifier  # type: ignore[import-untyped]
    except ImportError:
        out["xgboost_note"] = "skipped (xgboost not installed; pip install -r requirements.txt)"
        return out

    xgb = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        min_child_weight=1.0,
        tree_method="hist",
        random_state=random_state,
        n_jobs=n_jobs,
        eval_metric="logloss",
        scale_pos_weight=spw,
    )
    out["xgboost"] = _eval_sklearn_prob_classifier(
        xgb, X_train, y_train, X_val, y_val, X_test, y_test, thr_grid
    )
    out["xgboost_note"] = "ok"
    return out


__all__ = [
    "best_youden_threshold",
    "fit_rf_xgb_tabular",
]
