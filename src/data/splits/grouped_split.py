from __future__ import annotations

from typing import Tuple

import numpy as np


def grouped_train_val_test_masks(
    groups: np.ndarray,
    *,
    test_size: float = 0.2,
    val_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return boolean masks (train, val, test) so no group appears in more than one split.
    """
    rng = np.random.default_rng(random_state)
    unique = np.unique(groups)
    if len(unique) < 3:
        raise ValueError("Need at least 3 unique groups for train/val/test splits.")
    rng.shuffle(unique)
    n_g = len(unique)
    n_test = max(1, int(round(n_g * test_size)))
    n_val = max(1, int(round(n_g * val_size)))
    if n_test + n_val >= n_g:
        raise ValueError("test_size + val_size too large for number of groups.")
    test_gid = set(unique[:n_test])
    val_gid = set(unique[n_test : n_test + n_val])
    train_gid = set(unique[n_test + n_val :])
    mask_test = np.array([g in test_gid for g in groups], dtype=bool)
    mask_val = np.array([g in val_gid for g in groups], dtype=bool)
    mask_train = np.array([g in train_gid for g in groups], dtype=bool)
    return mask_train, mask_val, mask_test


def assert_no_group_leakage(
    groups: np.ndarray,
    mask_train: np.ndarray,
    mask_val: np.ndarray,
    mask_test: np.ndarray,
) -> None:
    """
    Raise ValueError if any group appears in multiple splits.
    """
    g_train = set(np.unique(groups[mask_train]))
    g_val = set(np.unique(groups[mask_val]))
    g_test = set(np.unique(groups[mask_test]))
    if g_train & g_val:
        raise ValueError("Leakage detected: train and val share group ids.")
    if g_train & g_test:
        raise ValueError("Leakage detected: train and test share group ids.")
    if g_val & g_test:
        raise ValueError("Leakage detected: val and test share group ids.")


def grouped_split_with_class_coverage(
    groups: np.ndarray,
    y: np.ndarray,
    *,
    test_size: float = 0.2,
    val_size: float = 0.2,
    random_state: int = 42,
    max_tries: int = 50,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Try multiple random seeds until val and test each contain at least one
    positive and one negative label.
    """
    y = np.asarray(y).astype(int)
    last_masks = None
    for i in range(max_tries):
        mt, mv, mte = grouped_train_val_test_masks(
            groups,
            test_size=test_size,
            val_size=val_size,
            random_state=random_state + i,
        )
        last_masks = (mt, mv, mte)
        yv = y[mv]
        yt = y[mte]
        if len(np.unique(yv)) >= 2 and len(np.unique(yt)) >= 2:
            return mt, mv, mte
    # fallback to last valid grouped split; caller can still proceed with warnings.
    return last_masks  # type: ignore[return-value]


__all__ = [
    "grouped_train_val_test_masks",
    "assert_no_group_leakage",
    "grouped_split_with_class_coverage",
]
