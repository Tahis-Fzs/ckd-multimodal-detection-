from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


CKD_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ExperimentConfig:
    random_state: int = 42
    test_size: float = 0.2
    val_size: float = 0.2
    output_dir: str = "outputs/runs"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def resolve_output_dir(self) -> Path:
        p = CKD_ROOT / self.output_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    def build_run_name(self, prefix: str) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{prefix}_{ts}"


__all__ = ["ExperimentConfig", "CKD_ROOT"]
