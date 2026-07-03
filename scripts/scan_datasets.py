#!/usr/bin/env python3
"""
Scan CKD Dataset/ and write DATASET_INVENTORY.md so NHANES / WESAD / MIMIC
layouts are visible without browsing huge trees.

Usage (from CKD Dataset/):
  python3 scripts/scan_datasets.py
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "DATASET_INVENTORY.md"
SKIP_DIR_NAMES = {".venv", "__pycache__", ".git", "site-packages"}


def should_skip_path(p: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in p.parts)


def humansize(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


def scan_tree(
    base: Path, max_depth: int | None = None, max_files_list: int = 40
) -> tuple[dict, list[str], int]:
    """Extension counts, sample relative paths, total bytes under base (skips .venv etc.)."""
    ext_counts: dict[str, int] = defaultdict(int)
    samples: list[str] = []
    total_bytes = 0
    base = base.resolve()
    if not base.is_dir():
        return {}, [], 0

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_path(path):
            continue
        try:
            rel = path.relative_to(base)
        except ValueError:
            continue
        if max_depth is not None and len(rel.parts) > max_depth:
            continue
        total_bytes += path.stat().st_size
        ext = path.suffix.lower() or "(no ext)"
        ext_counts[ext] += 1
        if len(samples) < max_files_list:
            samples.append(str(rel).replace("\\", "/"))

    return dict(sorted(ext_counts.items(), key=lambda x: -x[1])), sorted(samples), total_bytes


def list_immediate_dirs(path: Path) -> list[str]:
    if not path.is_dir():
        return []
    out = []
    for c in sorted(path.iterdir()):
        if should_skip_path(c):
            continue
        if c.is_dir():
            out.append(c.name + "/")
        elif c.is_file() and c.name not in {".DS_Store"}:
            out.append(c.name)
    return out


def main() -> None:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append("# CKD Dataset — auto inventory\n")
    lines.append(f"_Generated: {ts} (run `python3 scan_datasets.py` to refresh)_\n")
    lines.append(f"_Root: `{ROOT}`_\n")

    # Top-level
    lines.append("\n## Top-level entries\n")
    for name in list_immediate_dirs(ROOT):
        if name == "DATASET_INVENTORY.md":
            continue
        lines.append(f"- `{name}`\n")

    # NHANES
    nh = ROOT / "nhanes_ckd"
    lines.append("\n## NHANES (`nhanes_ckd/`)\n")
    if nh.is_dir():
        for sub in ("csv", "data"):
            p = nh / sub
            if p.is_dir():
                _, _, nbytes = scan_tree(p, max_depth=None, max_files_list=0)
                nfiles = sum(1 for f in p.rglob("*") if f.is_file() and not should_skip_path(f))
                lines.append(f"- **`{sub}/`**: {nfiles} files, total ~{humansize(nbytes)}\n")
        lines.append("\nSample `csv/` layout (first levels):\n\n```\n")
        csv_root = nh / "csv"
        if csv_root.is_dir():
            for cycle in sorted(csv_root.iterdir())[:6]:
                if cycle.is_dir():
                    kids = ", ".join(sorted(x.name for x in cycle.iterdir() if x.is_file())[:8])
                    lines.append(f"{cycle.name}/  [{kids}{'...' if sum(1 for _ in cycle.iterdir()) > 8 else ''}]\n")
        lines.append("```\n")
    else:
        lines.append("_Folder not found._\n")

    # WESAD
    wesad = ROOT / "WESAD"
    lines.append("\n## WESAD (`WESAD/`)\n")
    if wesad.is_dir():
        subjects = sorted(
            d for d in wesad.iterdir() if d.is_dir() and d.name.startswith("S") and d.name[1:].isdigit()
        )
        lines.append(f"- **Subject folders:** {len(subjects)} (`{', '.join(s.name for s in subjects[:5])}`" + ("…" if len(subjects) > 5 else "") + ")\n")
        pkls = list(wesad.rglob("*.pkl"))
        lines.append(f"- **`.pkl` files:** {len(pkls)}\n")
        for stem in ("S12",):
            if (wesad / stem).exists():
                lines.append(f"- Present: `{stem}/`\n")
        if not (wesad / "S12").exists():
            lines.append("- Note: official WESAD has no `S12`; missing folder is expected.\n")
    else:
        lines.append("_Folder not found._\n")

    # MIMIC
    mimic = ROOT / "mimic-iv-3.1"
    lines.append("\n## MIMIC-IV v3.1 (`mimic-iv-3.1/`)\n")
    if mimic.is_dir():
        children = list_immediate_dirs(mimic)
        lines.append("- **Immediate contents:** " + ", ".join(f"`{c}`" for c in children) + "\n")
        for module, desc in (("hosp", "hospital tables"), ("icu", "ICU tables")):
            mp = mimic / module
            if mp.is_dir():
                ext_c, samples, nb = scan_tree(mp, max_depth=None, max_files_list=15)
                lines.append(f"- **`{module}/`** ({desc}): ~{humansize(nb)}; extensions: {ext_c}\n")
                if samples:
                    lines.append("  - Sample files:\n")
                    for s in samples[:10]:
                        lines.append(f"    - `{s}`\n")
            else:
                lines.append(
                    f"- **`{module}/`**: _missing_ — unpack PhysioNet `mimic-iv-3.1` **{module}** `.csv.gz` files here.\n"
                )
    else:
        lines.append("_Folder not found._\n")

    lines.append(
        "\n---\n\nIf MIMIC `hosp/` and `icu/` are missing, Cursor search will not show patient-level tables until you extract the release.\n"
    )

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
