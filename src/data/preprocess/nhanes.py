from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd

from src.data.loaders.ckd_loaders import load_nhanes_cycle


def default_nhanes_demo_stems(cycle: str) -> Tuple[str, str]:
    """DEMO + BIOPRO table stems for each curated NHANES cycle folder."""
    if cycle == "2013-2014":
        return ("DEMO_H", "BIOPRO_H")
    if cycle == "2015-2016":
        return ("DEMO_I", "BIOPRO_I")
    if cycle == "2017-March2020_prepandemic":
        return ("P_DEMO", "P_BIOPRO")
    raise ValueError(f"Unknown cycle: {cycle}")


def merge_nhanes_tables(
    cycle: str,
    stems: Optional[Tuple[str, ...]] = None,
    max_rows: Optional[int] = None,
) -> pd.DataFrame:
    """Load all CSVs for a cycle from disk via load_nhanes_cycle; inner-merge on SEQN."""
    if stems is None:
        stems = default_nhanes_demo_stems(cycle)
    dfs = load_nhanes_cycle(cycle)
    missing = [s for s in stems if s not in dfs]
    if missing:
        raise KeyError(f"Missing tables in cycle {cycle}: {missing}. Have: {list(dfs)}")
    out = dfs[stems[0]]
    for s in stems[1:]:
        out = out.merge(dfs[s], on="SEQN", how="inner", suffixes=("", f"__{s}"))
    if max_rows is not None:
        out = out.sample(min(max_rows, len(out)), random_state=42) if len(out) else out
    return out


__all__ = [
    "default_nhanes_demo_stems",
    "merge_nhanes_tables",
]
