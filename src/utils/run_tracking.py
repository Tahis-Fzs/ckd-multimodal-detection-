from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def save_run_json(output_dir: Path, run_name: str, payload: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{run_name}.json"
    out_path.write_text(json.dumps(_json_safe(payload), indent=2))
    return out_path


__all__ = ["save_run_json"]
