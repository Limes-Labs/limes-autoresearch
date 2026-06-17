from __future__ import annotations

import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .backends import detect_backends
from .config import ExperimentConfig
from .ledger import parse_metrics, write_ledger_record


@dataclass(frozen=True)
class ExperimentResult:
    experiment: str
    status: str
    returncode: int | None
    metrics: dict[str, float]
    stdout: str
    stderr: str
    duration_seconds: float

    def to_record(self, command: list[str]) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "experiment": self.experiment,
            "command": command,
            "status": self.status,
            "returncode": self.returncode,
            "metrics": self.metrics,
            "duration_seconds": round(self.duration_seconds, 6),
            "backend": detect_backends().to_dict(),
        }


def run_experiment(config: ExperimentConfig, ledger_path: str | Path) -> ExperimentResult:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            config.command,
            cwd=config.cwd,
            text=True,
            capture_output=True,
            timeout=config.timeout_seconds,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
        status = "success" if completed.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        stdout = _coerce_output(exc.stdout)
        stderr = _coerce_output(exc.stderr)
        returncode = None
        status = "timeout"

    duration = time.monotonic() - started
    metrics = parse_metrics("\n".join([stdout, stderr]), config.metric_keys)
    result = ExperimentResult(
        experiment=config.name,
        status=status,
        returncode=returncode,
        metrics=metrics,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
    )
    write_ledger_record(ledger_path, result.to_record(config.command))
    return result


def _coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
