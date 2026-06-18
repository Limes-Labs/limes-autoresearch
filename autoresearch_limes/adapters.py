from __future__ import annotations

from copy import deepcopy
from typing import Any


_ADAPTERS: dict[str, dict[str, Any]] = {
    "eurobench": {
        "name_prefix": "eurobench",
        "command": [
            "python3",
            "-m",
            "eurobench",
            "run",
            "--suite",
            "TODO: replace-with-suite",
            "--model",
            "TODO: replace-with-model",
        ],
        "metric_keys": ["score", "pass_rate", "citation_accuracy", "elapsed_seconds"],
        "timeout_seconds": 1800,
        "notes": (
            "TODO: replace suite/model values. Keep public dev tasks separate from "
            "locked heldout tasks, and record the EuroBench dataset version."
        ),
    },
    "limes-parameter-golf": {
        "name_prefix": "parameter-golf",
        "command": [
            "python3",
            "-m",
            "parameter_golf",
            "benchmark",
            "--entry",
            "TODO: replace-with-entrypoint",
        ],
        "metric_keys": [
            "score",
            "compressed_size_bytes",
            "parameter_count",
            "train_seconds",
        ],
        "timeout_seconds": 1800,
        "notes": (
            "TODO: replace entrypoint. Charge parameter count, artifact size, "
            "training time, and optimizer overhead against the same budget."
        ),
    },
    "limes-nanogpt": {
        "name_prefix": "nanogpt",
        "command": [
            "python3",
            "train.py",
            "--config",
            "TODO: replace-with-config",
        ],
        "metric_keys": ["val_loss", "val_bpb", "train_loss", "tokens", "elapsed_seconds"],
        "timeout_seconds": 3600,
        "notes": (
            "TODO: replace config. Use fixed seeds, fixed train/validation/heldout "
            "boundaries, and replay candidates before promotion."
        ),
    },
}


def adapter_names() -> list[str]:
    return sorted(_ADAPTERS)


def build_adapter_config(name: str, experiment: str = "smoke") -> dict[str, Any]:
    if name not in _ADAPTERS:
        raise ValueError(f"Unknown adapter {name!r}; choose one of {adapter_names()}")

    template = deepcopy(_ADAPTERS[name])
    prefix = str(template.pop("name_prefix"))
    template["name"] = f"{prefix}-{experiment}"
    return template
