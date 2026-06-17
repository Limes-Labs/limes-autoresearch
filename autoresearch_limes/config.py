from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    command: list[str]
    metric_keys: list[str] = field(default_factory=lambda: ["val_bpb"])
    timeout_seconds: int | None = None
    cwd: str | None = None


def load_config(path: str | Path) -> ExperimentConfig:
    config_path = Path(path)
    data = _load_mapping(config_path)

    name = str(data.get("name") or config_path.stem)
    command = _normalize_command(data.get("command"))
    metric_keys = [str(item) for item in data.get("metric_keys", ["val_bpb"])]
    timeout_seconds = data.get("timeout_seconds")
    cwd = data.get("cwd")

    if timeout_seconds is not None:
        timeout_seconds = int(timeout_seconds)
    if cwd is not None:
        cwd = str(cwd)

    return ExperimentConfig(
        name=name,
        command=command,
        metric_keys=metric_keys,
        timeout_seconds=timeout_seconds,
        cwd=cwd,
    )


def _load_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix.lower() == ".toml":
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    if not isinstance(data, dict):
        raise ValueError("Experiment config must be a mapping")
    return data


def _normalize_command(value: Any) -> list[str]:
    if value is None:
        raise ValueError("Experiment config requires a command")

    if isinstance(value, str):
        import shlex

        command = shlex.split(value)
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        command = list(value)
    else:
        raise ValueError("Experiment command must be a string or list of strings")

    if not command:
        raise ValueError("Experiment command cannot be empty")
    return command
