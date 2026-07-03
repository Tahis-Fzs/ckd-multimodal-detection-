#!/usr/bin/env python3
"""
Thesis Figure 3.6 — WESAD wrist window (BVP / EDA / TEMP / ACC).

Usage (from CKD Dataset):
  MPLCONFIGDIR="$(pwd)/.mplconfig" MPLBACKEND=Agg .venv312/bin/python \\
    Results/figures/make_figure_3_6_wesad_window.py \\
    --wesad_root "/Users/md.shadmantahsin/Desktop/STUDY/Dataset/WESAD" \\
    --subject S2 \\
    --window_samples 1920 \\
    --window_index 0 \\
    --out "Results/figures/figure_3_6_wesad_window.png"
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

LABEL_MAP = {0: "transient", 1: "baseline", 2: "stress", 3: "amusement", 4: "meditation", 5: "unknown"}


def load_subject(wesad_root: Path, subject: str) -> dict:
    sid = subject if subject.startswith("S") else f"S{subject}"
    pkl_path = wesad_root / sid / f"{sid}.pkl"
    if not pkl_path.exists():
        raise FileNotFoundError(f"WESAD pickle not found: {pkl_path}")
    with open(pkl_path, "rb") as f:
        return pickle.load(f, encoding="latin1")


def window_starts(n: int, window_samples: int, stride: int, max_windows: int) -> list[int]:
    starts = list(range(0, max(n - window_samples, 0) + 1, stride))
    if len(starts) > max_windows:
        pick = np.linspace(0, len(starts) - 1, max_windows, dtype=int)
        starts = [starts[i] for i in pick]
    return starts


def majority_label(label: np.ndarray, start: int, end: int, n_bvp: int) -> int:
    l0 = int(start * len(label) / n_bvp)
    l1 = int(end * len(label) / n_bvp)
    l1 = min(max(l1, l0 + 1), len(label))
    seg = label[l0:l1]
    vals, counts = np.unique(seg, return_counts=True)
    return int(vals[np.argmax(counts)])


def plot_window(
    subject_dict: dict,
    window_samples: int,
    window_index: int,
    stride: int,
    max_windows: int,
    out: Path,
) -> Path:
    wrist = subject_dict["signal"]["wrist"]
    label = np.asarray(subject_dict["label"]).reshape(-1)
    sid = str(subject_dict.get("subject", "unknown"))

    bvp = np.asarray(wrist["BVP"], dtype=float).reshape(-1)
    eda = np.asarray(wrist["EDA"], dtype=float).reshape(-1)
    temp = np.asarray(wrist["TEMP"], dtype=float).reshape(-1)
    acc = np.asarray(wrist["ACC"], dtype=float)
    acc_mag = np.linalg.norm(acc, axis=1) if acc.ndim == 2 else acc.reshape(-1)

    n = len(bvp)
    starts = window_starts(n, window_samples, stride, max_windows)
    if not starts:
        raise ValueError(f"No windows for subject {sid} (n={n}, window={window_samples})")
    if window_index < 0 or window_index >= len(starts):
        raise IndexError(f"window_index {window_index} out of range (0..{len(starts) - 1})")

    start = starts[window_index]
    end = start + window_samples
    maj = majority_label(label, start, end, n)
    label_name = LABEL_MAP.get(maj, str(maj))

    # ~64 Hz BVP in WESAD wrist stream
    t = np.arange(window_samples) / 64.0

    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    series = [
        ("BVP", bvp[start:end], "#1f77b4"),
        ("EDA", eda[min(start, len(eda) - 1) : min(end, len(eda))], "#ff7f0e"),
        ("TEMP", temp[min(start, len(temp) - 1) : min(end, len(temp))], "#2ca02c"),
        ("ACC magnitude", acc_mag[start:end], "#9467bd"),
    ]

    for ax, (name, y, color) in zip(axes, series):
        x = t[: len(y)]
        ax.plot(x, y, color=color, linewidth=0.8)
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.25)

    axes[-1].set_xlabel("Time within window (s)")
    fig.suptitle(
        f"WESAD wrist window — {sid} | index {window_index} | "
        f"samples {start}:{end} | majority label: {label_name} ({maj})",
        fontsize=11,
    )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")

    paper_copy = out.resolve().parents[2] / "paper_assets" / "figures" / out.name
    if paper_copy.parent.exists() or (out.resolve().parents[2] / "paper_assets").exists():
        paper_copy.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(out, paper_copy)

    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Figure 3.6 — WESAD wrist window plot")
    ap.add_argument("--wesad_root", type=Path, required=True)
    ap.add_argument("--subject", type=str, default="S2")
    ap.add_argument("--window_samples", type=int, default=1920)
    ap.add_argument("--stride", type=int, default=960)
    ap.add_argument("--max_windows", type=int, default=120)
    ap.add_argument("--window_index", type=int, default=0)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("Results/figures/figure_3_6_wesad_window.png"),
    )
    args = ap.parse_args()

    subject_dict = load_subject(args.wesad_root, args.subject)
    out = plot_window(
        subject_dict,
        window_samples=args.window_samples,
        window_index=args.window_index,
        stride=args.stride,
        max_windows=args.max_windows,
        out=args.out,
    )
    print(f"Saved: {out.resolve()}")


if __name__ == "__main__":
    main()
