from __future__ import annotations

import importlib.util
import platform
import sys
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BackendReport:
    os_name: str
    machine: str
    python_version: str
    torch_available: bool
    torch_cuda_available: bool
    torch_mps_available: bool
    mlx_available: bool
    preferred: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _torch_flags() -> tuple[bool, bool, bool]:
    if importlib.util.find_spec("torch") is None:
        return False, False, False

    try:
        import torch  # type: ignore[import-not-found]
    except Exception:
        return False, False, False

    cuda_available = bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    mps_backend = getattr(getattr(torch, "backends", None), "mps", None)
    mps_available = bool(mps_backend and mps_backend.is_available())
    return True, cuda_available, mps_available


def detect_backends() -> BackendReport:
    torch_available, torch_cuda_available, torch_mps_available = _torch_flags()
    mlx_available = importlib.util.find_spec("mlx") is not None

    if torch_cuda_available:
        preferred = "cuda"
    elif mlx_available:
        preferred = "mlx"
    elif torch_mps_available:
        preferred = "mps"
    else:
        preferred = "cpu"

    return BackendReport(
        os_name=platform.system(),
        machine=platform.machine(),
        python_version=sys.version.split()[0],
        torch_available=torch_available,
        torch_cuda_available=torch_cuda_available,
        torch_mps_available=torch_mps_available,
        mlx_available=mlx_available,
        preferred=preferred,
    )
