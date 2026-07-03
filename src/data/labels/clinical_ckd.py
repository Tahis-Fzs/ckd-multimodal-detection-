from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


def compute_egfr_ckd_epi_2021(
    creat_mg_dl: np.ndarray,
    age_years: np.ndarray,
    female_flag: np.ndarray,
) -> np.ndarray:
    """
    Race-free CKD-EPI 2021 creatinine equation (single time-point estimate).
    """
    kappa = np.where(female_flag, 0.7, 0.9)
    alpha = np.where(female_flag, -0.241, -0.302)
    scr_k = creat_mg_dl / kappa
    min_term = np.minimum(scr_k, 1.0) ** alpha
    max_term = np.maximum(scr_k, 1.0) ** (-1.2)
    sex_factor = np.where(female_flag, 1.012, 1.0)
    egfr = 142.0 * min_term * max_term * (0.9938 ** age_years) * sex_factor
    return egfr


def nhanes_clinical_ckd_label(
    df: pd.DataFrame,
    *,
    creat_col: str = "LBXSCR",
    age_col: str = "RIDAGEYR",
    sex_col: str = "RIAGENDR",
    acr_col: Optional[str] = "URDACT",
    require_both_markers: bool = False,
) -> Tuple[pd.Series, Dict[str, float]]:
    """
    Build a clinically aligned binary CKD-risk proxy label from NHANES rows.

    Rule:
      Default: CKD-risk = (eGFR < 60) OR (ACR >= 30 mg/g, if available).
      Strict:  CKD-risk = (eGFR < 60) AND (ACR >= 30 mg/g, if available).

    Important:
      This is still a single-visit proxy, not persistence-confirmed CKD diagnosis.
    """
    required = [creat_col, age_col, sex_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns for clinical CKD label: {missing}")

    x = df.copy()
    x = x.dropna(subset=required)
    if x.empty:
        raise ValueError("No rows left after dropping NA for clinical label requirements.")

    creat = x[creat_col].to_numpy(dtype=float)
    age = x[age_col].to_numpy(dtype=float)
    # NHANES RIAGENDR: 1=male, 2=female
    female = (x[sex_col].to_numpy() == 2)

    egfr = compute_egfr_ckd_epi_2021(creat, age, female)
    egfr_ckd = egfr < 60.0

    has_acr = acr_col is not None and acr_col in x.columns
    if has_acr:
        acr = x[acr_col].to_numpy(dtype=float)
        acr_ckd = acr >= 30.0
        if require_both_markers:
            y = (egfr_ckd & acr_ckd).astype(int)
        else:
            y = (egfr_ckd | acr_ckd).astype(int)
        acr_non_missing = float(np.mean(~np.isnan(acr)))
    else:
        y = egfr_ckd.astype(int)
        acr_non_missing = 0.0

    label = pd.Series(y, index=x.index, name="ckd_risk_clinical")
    meta = {
        "rows_used": float(len(x)),
        "egfr_lt_60_rate": float(np.mean(egfr_ckd)),
        "used_acr": float(1.0 if has_acr else 0.0),
        "acr_non_missing_rate": acr_non_missing,
        "positive_rate": float(np.mean(y)),
        "rule_mode": float(1.0 if require_both_markers else 0.0),
    }
    return label, meta


def persistence_label_from_flag_series(
    df: pd.DataFrame,
    *,
    patient_col: str,
    time_col: str,
    abnormal_flag_col: str,
    min_abnormal_visits: int = 2,
    min_days_apart: int = 90,
) -> pd.Series:
    """
    Generic persistence logic for longitudinal cohorts.

    A patient is positive if they have >= min_abnormal_visits abnormal visits
    with first and last abnormal visits at least `min_days_apart` apart.
    """
    if patient_col not in df.columns or time_col not in df.columns or abnormal_flag_col not in df.columns:
        raise KeyError("Missing required columns for persistence labeling.")

    x = df[[patient_col, time_col, abnormal_flag_col]].copy()
    x = x.dropna(subset=[patient_col, time_col, abnormal_flag_col])
    x[time_col] = pd.to_datetime(x[time_col], errors="coerce")
    x = x.dropna(subset=[time_col])
    x[abnormal_flag_col] = x[abnormal_flag_col].astype(bool)

    def _patient_positive(g: pd.DataFrame) -> int:
        ab = g.loc[g[abnormal_flag_col], time_col].sort_values()
        if len(ab) < min_abnormal_visits:
            return 0
        days = (ab.iloc[-1] - ab.iloc[0]).days
        return int(days >= min_days_apart)

    out = x.groupby(patient_col, as_index=True).apply(_patient_positive)
    out.name = "ckd_persistent_label"
    return out


__all__ = [
    "compute_egfr_ckd_epi_2021",
    "nhanes_clinical_ckd_label",
    "persistence_label_from_flag_series",
]
