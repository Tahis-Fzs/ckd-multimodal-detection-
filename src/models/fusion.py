from __future__ import annotations

from typing import Optional

import numpy as np


def _check_2d(name: str, arr: np.ndarray) -> None:
    if arr.ndim != 2:
        raise ValueError(f"{name} must be 2D (n, d). Got shape={arr.shape}")


def fuse_embeddings(
    z_ehr: np.ndarray,
    z_ecg: Optional[np.ndarray] = None,
    z_wear: Optional[np.ndarray] = None,
    *,
    z_ecg_dim: int = 0,
    z_wear_dim: int = 0,
) -> np.ndarray:
    """
    Concatenate modality embeddings with explicit shape safety checks.

    - `z_ehr` is required and defines batch size n.
    - Optional modalities can be None. If None, zero blocks are used when
      expected dims (`z_ecg_dim`/`z_wear_dim`) are provided.
    """
    _check_2d("z_ehr", z_ehr)
    n = z_ehr.shape[0]
    blocks = [z_ehr]

    if z_ecg is not None:
        _check_2d("z_ecg", z_ecg)
        if z_ecg.shape[0] != n:
            raise ValueError(f"Batch mismatch: z_ehr n={n}, z_ecg n={z_ecg.shape[0]}")
        blocks.append(z_ecg)
    elif z_ecg_dim > 0:
        blocks.append(np.zeros((n, z_ecg_dim), dtype=z_ehr.dtype))

    if z_wear is not None:
        _check_2d("z_wear", z_wear)
        if z_wear.shape[0] != n:
            raise ValueError(f"Batch mismatch: z_ehr n={n}, z_wear n={z_wear.shape[0]}")
        blocks.append(z_wear)
    elif z_wear_dim > 0:
        blocks.append(np.zeros((n, z_wear_dim), dtype=z_ehr.dtype))

    return np.hstack(blocks)


__all__ = ["fuse_embeddings"]
