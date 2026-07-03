from __future__ import annotations

import pandas as pd


def default_nhanes_creatinine_col(_cycle: str) -> str:
    """
    Serum creatinine column used in BIOPRO-style NHANES files (verify in codebook).
    2013-2020 prepandemic BIOPRO/P_BIOPRO typically use LBXSCR (mg/dL).
    """
    return "LBXSCR"


def nhanes_demo_label_from_creatinine(
    df: pd.DataFrame,
    creat_col: str = "LBXSCR",
) -> pd.Series:
    """
    Demo-only binary outcome: creatinine above cohort median.

    This is intentionally a placeholder label for pipeline validation and should be
    replaced by guideline-based CKD definitions (e.g., eGFR + albuminuria) for
    thesis-grade clinical conclusions.
    """
    if creat_col not in df.columns:
        raise KeyError(f"Column {creat_col} not in dataframe; NHANES cycle may use another name.")
    return (df[creat_col] > df[creat_col].median()).astype(int)


__all__ = [
    "default_nhanes_creatinine_col",
    "nhanes_demo_label_from_creatinine",
]
