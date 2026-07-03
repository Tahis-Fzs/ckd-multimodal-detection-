#!/usr/bin/env python3
"""
Small PyTorch building blocks for tabular EHR-style inputs.

Install: pip install -r requirements.txt  (see PyTorch docs for your OS/GPU).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
except ImportError as e:  # pragma: no cover
    torch = None  # type: ignore
    nn = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None


def _require_torch() -> None:
    if _IMPORT_ERROR is not None or torch is None:
        raise ImportError(
            "PyTorch is required. Install with: pip install -r requirements.txt\n"
            f"Original error: {_IMPORT_ERROR}"
        )


if _IMPORT_ERROR is None:

    class TabularMLP(nn.Module):  # type: ignore[misc, name-defined]
        """Simple MLP for numeric feature matrix (e.g. NHANES / flattened EHR)."""

        def __init__(
            self,
            n_features: int,
            hidden: Tuple[int, ...] = (128, 64),
            dropout: float = 0.2,
            n_classes: int = 2,
        ) -> None:
            super().__init__()
            layers: List[nn.Module] = []
            d = n_features
            for h in hidden:
                layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
                d = h
            layers.append(nn.Linear(d, n_classes))
            self.net = nn.Sequential(*layers)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    class ResidualBlock(nn.Module):  # type: ignore[misc, name-defined]
        """Residual MLP block for tabular features."""

        def __init__(self, d: int, dropout: float = 0.1) -> None:
            super().__init__()
            self.fc1 = nn.Linear(d, d)
            self.fc2 = nn.Linear(d, d)
            self.act = nn.ReLU()
            self.drop = nn.Dropout(dropout)
            self.norm = nn.LayerNorm(d)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            h = self.fc1(x)
            h = self.act(h)
            h = self.drop(h)
            h = self.fc2(h)
            return self.norm(self.act(x + h))

    class TabularResMLP(nn.Module):  # type: ignore[misc, name-defined]
        """
        Residual MLP for tabular data.
        Projects to hidden dim and applies residual blocks before classification.
        """

        def __init__(
            self,
            n_features: int,
            d_model: int = 128,
            n_blocks: int = 3,
            dropout: float = 0.1,
            n_classes: int = 2,
        ) -> None:
            super().__init__()
            self.in_proj = nn.Sequential(
                nn.Linear(n_features, d_model),
                nn.ReLU(),
                nn.Dropout(dropout),
            )
            self.blocks = nn.Sequential(*[ResidualBlock(d_model, dropout=dropout) for _ in range(n_blocks)])
            self.head = nn.Linear(d_model, n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            h = self.in_proj(x)
            h = self.blocks(h)
            return self.head(h)

else:

    class TabularMLP:  # type: ignore[too-few-public-methods]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _require_torch()
            raise RuntimeError("unreachable")

    class TabularResMLP:  # type: ignore[too-few-public-methods]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _require_torch()
            raise RuntimeError("unreachable")


@dataclass
class TrainResult:
    history: Dict[str, List[float]]
    model_state: Dict[str, Any]
    best_val_auc: float


def train_tabular_mlp(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    *,
    hidden: Tuple[int, ...] = (128, 64),
    dropout: float = 0.2,
    epochs: int = 40,
    batch_size: int = 64,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: Optional[str] = None,
    save_path: Optional[Path] = None,
    seed: int = 42,
) -> TrainResult:
    """
    Train `TabularMLP` with Adam + cross-entropy; track train loss and val AUROC if sklearn available.

    X_* : float32 (n, n_features), NaNs should be imputed before calling.
    y_* : int64 (n,) with values 0..C-1 (binary: 0,1).
    """
    _require_torch()
    torch.manual_seed(seed)
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

    Xt = torch.from_numpy(np.ascontiguousarray(X_train, dtype=np.float32))
    yt = torch.from_numpy(np.ascontiguousarray(y_train, dtype=np.int64))
    Xv = torch.from_numpy(np.ascontiguousarray(X_val, dtype=np.float32))
    yv = torch.from_numpy(np.ascontiguousarray(y_val, dtype=np.int64))

    ds = TensorDataset(Xt, yt)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

    n_features = X_train.shape[1]
    n_classes = int(y_train.max()) + 1
    model = TabularMLP(n_features, hidden=hidden, dropout=dropout, n_classes=n_classes).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    history: Dict[str, List[float]] = {"train_loss": [], "val_auc": []}
    best_auc = float("-inf")
    best_state: Dict[str, Any] = {
        k: v.detach().cpu().clone() for k, v in model.state_dict().items()
    }

    try:
        from sklearn.metrics import roc_auc_score
    except ImportError:
        roc_auc_score = None  # type: ignore

    for ep in range(epochs):
        model.train()
        losses = []
        for xb, yb in dl:
            xb, yb = xb.to(dev), yb.to(dev)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
            losses.append(loss.item())
        history["train_loss"].append(float(np.mean(losses)) if losses else 0.0)

        model.eval()
        with torch.no_grad():
            logits_v = model(Xv.to(dev)).cpu().numpy()
        if roc_auc_score is not None and n_classes == 2:
            prob = softmax_rows(logits_v)[:, 1]
            try:
                auc = float(roc_auc_score(y_val, prob))
            except ValueError:
                auc = float("nan")
        else:
            auc = float("nan")
        history["val_auc"].append(auc)
        if not np.isnan(auc) and auc > best_auc:
            best_auc = auc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model": model.state_dict(), "n_features": n_features, "hidden": hidden, "n_classes": n_classes}, save_path)

    return TrainResult(history=history, model_state=best_state, best_val_auc=best_auc)


def train_tabular_resmlp(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    *,
    d_model: int = 128,
    n_blocks: int = 3,
    dropout: float = 0.1,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 8e-4,
    weight_decay: float = 1e-4,
    device: Optional[str] = None,
    save_path: Optional[Path] = None,
    seed: int = 42,
) -> TrainResult:
    """
    Train `TabularResMLP` with AdamW + cross-entropy; track train loss and val AUROC.
    """
    _require_torch()
    torch.manual_seed(seed)
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

    Xt = torch.from_numpy(np.ascontiguousarray(X_train, dtype=np.float32))
    yt = torch.from_numpy(np.ascontiguousarray(y_train, dtype=np.int64))
    Xv = torch.from_numpy(np.ascontiguousarray(X_val, dtype=np.float32))

    ds = TensorDataset(Xt, yt)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

    n_features = X_train.shape[1]
    n_classes = int(y_train.max()) + 1
    model = TabularResMLP(
        n_features=n_features,
        d_model=d_model,
        n_blocks=n_blocks,
        dropout=dropout,
        n_classes=n_classes,
    ).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    history: Dict[str, List[float]] = {"train_loss": [], "val_auc": []}
    best_auc = float("-inf")
    best_state: Dict[str, Any] = {
        k: v.detach().cpu().clone() for k, v in model.state_dict().items()
    }

    try:
        from sklearn.metrics import roc_auc_score
    except ImportError:
        roc_auc_score = None  # type: ignore

    for _ in range(epochs):
        model.train()
        losses = []
        for xb, yb in dl:
            xb, yb = xb.to(dev), yb.to(dev)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
            losses.append(loss.item())
        history["train_loss"].append(float(np.mean(losses)) if losses else 0.0)

        model.eval()
        with torch.no_grad():
            logits_v = model(Xv.to(dev)).cpu().numpy()
        if roc_auc_score is not None and n_classes == 2:
            prob = softmax_rows(logits_v)[:, 1]
            try:
                auc = float(roc_auc_score(y_val, prob))
            except ValueError:
                auc = float("nan")
        else:
            auc = float("nan")
        history["val_auc"].append(auc)
        if not np.isnan(auc) and auc > best_auc:
            best_auc = auc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model": model.state_dict(),
                "n_features": n_features,
                "d_model": d_model,
                "n_blocks": n_blocks,
                "dropout": dropout,
                "n_classes": n_classes,
            },
            save_path,
        )

    return TrainResult(history=history, model_state=best_state, best_val_auc=best_auc)


def softmax_rows(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)
