from __future__ import annotations

import argparse
import pickle
import warnings
from pathlib import Path
from typing import Dict, Iterator, Optional

import pandas as pd

CKD_ROOT = Path(__file__).resolve().parents[3]
NHANES_CSV = CKD_ROOT / "nhanes_ckd" / "csv"
WESAD_ROOT = CKD_ROOT / "WESAD"
MIMIC_ROOT = CKD_ROOT / "mimic-iv-3.1"
MIMIC_HOSP = MIMIC_ROOT / "hosp"
MIMIC_HOSP_CSV = MIMIC_HOSP / "CSV"
MIMIC_ICU = MIMIC_ROOT / "icu"
MIMIC_ED_ROOT = CKD_ROOT / "mimic-iv-ed-2.2" / "ed"

NHANES_CYCLES = (
    "2013-2014",
    "2015-2016",
    "2017-March2020_prepandemic",
)


def load_nhanes_cycle(cycle: str, nrows: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    folder = NHANES_CSV / cycle
    if not folder.is_dir():
        raise FileNotFoundError(f"NHANES cycle folder not found: {folder}")
    out: Dict[str, pd.DataFrame] = {}
    for path in sorted(folder.glob("*.csv")):
        out[path.stem] = pd.read_csv(path, nrows=nrows, low_memory=False)
    return out


def find_mimic_table_path(module: str, table_stem: str) -> Path:
    if module not in {"hosp", "icu"}:
        raise ValueError("module must be 'hosp' or 'icu'")

    candidates: list[Path] = []
    if module == "hosp":
        candidates.extend(
            [
                MIMIC_HOSP / f"{table_stem}.csv",
                MIMIC_HOSP / f"{table_stem}.csv.gz",
                MIMIC_HOSP_CSV / f"{table_stem}.csv",
                MIMIC_HOSP_CSV / f"{table_stem}.csv.gz",
            ]
        )
    else:
        candidates.extend([MIMIC_ICU / f"{table_stem}.csv", MIMIC_ICU / f"{table_stem}.csv.gz"])

    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(f"MIMIC {module} table not found: {table_stem} (tried: {candidates[:4]}...)")


def load_mimic_table(
    module: str,
    table_stem: str,
    nrows: Optional[int] = None,
    chunksize: Optional[int] = None,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    path = find_mimic_table_path(module, table_stem)
    comp = "gzip" if path.suffix == ".gz" else None
    kwargs = dict(low_memory=False)
    if nrows is not None:
        kwargs["nrows"] = nrows
    if chunksize is not None:
        return pd.read_csv(path, compression=comp, chunksize=chunksize, **kwargs)
    return pd.read_csv(path, compression=comp, **kwargs)


def find_mimic_ed_table_path(table_stem: str) -> Path:
    if not MIMIC_ED_ROOT.is_dir():
        raise FileNotFoundError(f"MIMIC-IV-ED folder not found: {MIMIC_ED_ROOT}")
    candidates = [MIMIC_ED_ROOT / f"{table_stem}.csv.gz", MIMIC_ED_ROOT / f"{table_stem}.csv"]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(f"MIMIC-IV-ED table not found: {table_stem} under {MIMIC_ED_ROOT}")


def load_mimic_ed_table(
    table_stem: str,
    nrows: Optional[int] = None,
    chunksize: Optional[int] = None,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    path = find_mimic_ed_table_path(table_stem)
    comp = "gzip" if path.suffix == ".gz" or str(path).endswith(".csv.gz") else None
    kwargs = dict(low_memory=False)
    if nrows is not None:
        kwargs["nrows"] = nrows
    if chunksize is not None:
        return pd.read_csv(path, compression=comp, chunksize=chunksize, **kwargs)
    return pd.read_csv(path, compression=comp, **kwargs)


def resolve_mimic_ecg_root() -> Path:
    # Include the downloaded demo folder pattern so Step 2 works immediately.
    candidates = [
        CKD_ROOT / "mimic-iv-ecg",
        CKD_ROOT / "mimic-iv-ecg-1.0",
        CKD_ROOT / "mimic-iv-ecg-demo-diagnostic-electrocardiogram-matched-subset-demo-0.1",
    ]
    markers = ("record_list.csv.gz", "record_list.csv", "machine_measurements.csv.gz", "machine_measurements.csv")
    for base in candidates:
        if not base.is_dir():
            continue
        for marker in markers:
            if (base / marker).is_file():
                return base
        if any(base.glob("*.csv")) or any(base.glob("*.csv.gz")):
            return base
    raise FileNotFoundError(
        "MIMIC-IV-ECG folder not found. Expected one of: "
        + ", ".join(str(p) for p in candidates)
    )


def find_mimic_ecg_table_path(table_stem: str) -> Path:
    base = resolve_mimic_ecg_root()
    candidates = [base / f"{table_stem}.csv.gz", base / f"{table_stem}.csv"]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(f"MIMIC-IV-ECG table not found: {table_stem} under {base}")


def load_mimic_ecg_table(
    table_stem: str,
    nrows: Optional[int] = None,
    chunksize: Optional[int] = None,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    path = find_mimic_ecg_table_path(table_stem)
    comp = "gzip" if path.suffix == ".gz" or str(path).endswith(".csv.gz") else None
    kwargs = dict(low_memory=False)
    if nrows is not None:
        kwargs["nrows"] = nrows
    if chunksize is not None:
        return pd.read_csv(path, compression=comp, chunksize=chunksize, **kwargs)
    return pd.read_csv(path, compression=comp, **kwargs)


def load_wesad_pkl(subject_id: str) -> object:
    sid = subject_id.upper() if subject_id.upper().startswith("S") else f"S{subject_id}"
    pkl = WESAD_ROOT / sid / f"{sid}.pkl"
    if not pkl.is_file():
        raise FileNotFoundError(f"WESAD pickle not found: {pkl}")
    with open(pkl, "rb") as f:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"dtype\(\): align should be passed as Python or NumPy boolean.*",
                    category=Warning,
                )
                return pickle.load(f)
        except (UnicodeDecodeError, pickle.UnpicklingError):
            f.seek(0)
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"dtype\(\): align should be passed as Python or NumPy boolean.*",
                    category=Warning,
                )
                return pickle.load(f, encoding="latin1")


def peek_all(nhanes_nrows: int = 3, mimic_nrows: int = 5) -> None:
    print("=== NHANES (first cycle sample) ===")
    c0 = NHANES_CYCLES[0]
    try:
        dfs = load_nhanes_cycle(c0, nrows=nhanes_nrows)
        for name, df in dfs.items():
            print(f"  {c0}/{name}.csv  shape={df.shape}  cols={list(df.columns)[:6]}...")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== WESAD (first subject with .pkl) ===")
    pkls = sorted(WESAD_ROOT.glob("S*/S*.pkl"))
    if not pkls:
        print("  No .pkl found")
    else:
        p = pkls[0]
        try:
            obj = load_wesad_pkl(p.parent.name)
            print(f"  {p.relative_to(CKD_ROOT)}  type={type(obj)}")
            if isinstance(obj, dict):
                print(f"  keys (sample): {list(obj.keys())[:12]}")
        except Exception as e:
            print(f"  Error loading {p}: {e}")

    print("\n=== MIMIC hosp (admissions if present) ===")
    try:
        df = load_mimic_table("hosp", "admissions", nrows=mimic_nrows)
        print(f"  admissions  shape={df.shape}  cols={list(df.columns)[:8]}...")
    except FileNotFoundError as e:
        print(f"  {e}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== MIMIC icu (d_items if present) ===")
    try:
        df = load_mimic_table("icu", "d_items", nrows=mimic_nrows)
        print(f"  d_items  shape={df.shape}  cols={list(df.columns)[:8]}...")
    except FileNotFoundError as e:
        print(f"  {e}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== MIMIC-IV-ED (edstays if present) ===")
    try:
        df = load_mimic_ed_table("edstays", nrows=mimic_nrows)
        print(f"  edstays  shape={df.shape}  cols={list(df.columns)[:8]}...")
    except FileNotFoundError as e:
        print(f"  {e}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== MIMIC-IV-ECG metadata (record_list if present) ===")
    try:
        df = load_mimic_ecg_table("record_list", nrows=mimic_nrows)
        print(f"  record_list  shape={df.shape}  cols={list(df.columns)[:8]}...")
    except FileNotFoundError:
        try:
            df = load_mimic_ecg_table("machine_measurements", nrows=mimic_nrows)
            print(f"  machine_measurements  shape={df.shape}  cols={list(df.columns)[:8]}...")
        except FileNotFoundError as e:
            print(f"  {e}")
    except Exception as e:
        print(f"  Error: {e}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Load CKD Dataset (NHANES / WESAD / MIMIC-IV / MIMIC-IV-ED / MIMIC-IV-ECG)"
    )
    ap.add_argument("--peek", action="store_true", help="Print small samples from each source")
    ap.add_argument("--nhanes-cycle", choices=NHANES_CYCLES, help="Load full NHANES cycle into memory (careful: use --nrows)")
    ap.add_argument("--nrows", type=int, default=None, help="Limit rows for NHANES / MIMIC single-table reads")
    ap.add_argument("--mimic-module", choices=["hosp", "icu"], default="hosp")
    ap.add_argument("--mimic-table", type=str, default=None, help="e.g. admissions, labevents")
    ap.add_argument(
        "--mimic-ed-table",
        type=str,
        default=None,
        help="MIMIC-IV-ED table under mimic-iv-ed-2.2/ed/, e.g. edstays, triage",
    )
    ap.add_argument(
        "--mimic-ecg-table",
        type=str,
        default=None,
        help="MIMIC-IV-ECG metadata CSV under mimic-iv-ecg/, e.g. record_list, machine_measurements",
    )
    ap.add_argument("--chunksize", type=int, default=None, help="Stream MIMIC in chunks (large tables)")
    ap.add_argument("--wesad", type=str, default=None, help="Subject id e.g. S10")
    args = ap.parse_args()

    if args.peek:
        peek_all()
        return

    if args.wesad:
        obj = load_wesad_pkl(args.wesad)
        print(f"Loaded WESAD {args.wesad}: {type(obj)}")
        if isinstance(obj, dict):
            print("Keys:", list(obj.keys()))
        return

    if args.mimic_ed_table:
        if args.chunksize:
            it = load_mimic_ed_table(args.mimic_ed_table, chunksize=args.chunksize)
            chunk = next(iter(it))
            print(f"First chunk shape: {chunk.shape}\nColumns: {list(chunk.columns)[:15]}")
        else:
            df = load_mimic_ed_table(args.mimic_ed_table, nrows=args.nrows)
            print(df)
            print(f"shape: {df.shape}")
        return

    if args.mimic_ecg_table:
        if args.chunksize:
            it = load_mimic_ecg_table(args.mimic_ecg_table, chunksize=args.chunksize)
            chunk = next(iter(it))
            print(f"First chunk shape: {chunk.shape}\nColumns: {list(chunk.columns)[:15]}")
        else:
            df = load_mimic_ecg_table(args.mimic_ecg_table, nrows=args.nrows)
            print(df)
            print(f"shape: {df.shape}")
        return

    if args.nhanes_cycle:
        dfs = load_nhanes_cycle(args.nhanes_cycle, nrows=args.nrows)
        for key, df in dfs.items():
            print(f"{key}: {df.shape}")
        return

    if args.mimic_table:
        if args.chunksize:
            it = load_mimic_table(args.mimic_module, args.mimic_table, chunksize=args.chunksize)
            chunk = next(iter(it))
            print(f"First chunk shape: {chunk.shape}\nColumns: {list(chunk.columns)[:15]}")
        else:
            df = load_mimic_table(args.mimic_module, args.mimic_table, nrows=args.nrows)
            print(df)
            print(f"shape: {df.shape}")
        return

    ap.print_help()


__all__ = [
    "CKD_ROOT",
    "NHANES_CSV",
    "WESAD_ROOT",
    "MIMIC_ROOT",
    "MIMIC_HOSP",
    "MIMIC_HOSP_CSV",
    "MIMIC_ICU",
    "MIMIC_ED_ROOT",
    "NHANES_CYCLES",
    "load_nhanes_cycle",
    "find_mimic_table_path",
    "load_mimic_table",
    "find_mimic_ed_table_path",
    "load_mimic_ed_table",
    "resolve_mimic_ecg_root",
    "find_mimic_ecg_table_path",
    "load_mimic_ecg_table",
    "load_wesad_pkl",
    "peek_all",
    "main",
]
