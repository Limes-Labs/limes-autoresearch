from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

_METRIC_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>-?\d+(?:\.\d+)?)")


def parse_metrics(text: str, metric_keys: Iterable[str] | None = None) -> dict[str, float]:
    allowed = set(metric_keys) if metric_keys is not None else None
    metrics: dict[str, float] = {}

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            _merge_json_metrics(stripped, metrics, allowed)

        for match in _METRIC_RE.finditer(line):
            key = match.group("key")
            if allowed is None or key in allowed:
                metrics[key] = float(match.group("value"))

    return metrics


def write_ledger_record(path: str | Path, record: dict[str, Any]) -> None:
    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_ledger(path: str | Path) -> list[dict[str, Any]]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return []

    records = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _merge_json_metrics(
    line: str, metrics: dict[str, float], allowed: set[str] | None
) -> None:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return

    raw_metrics = payload.get("metrics") if isinstance(payload, dict) else None
    if not isinstance(raw_metrics, dict):
        raw_metrics = payload if isinstance(payload, dict) else {}

    for key, value in raw_metrics.items():
        if allowed is not None and key not in allowed:
            continue
        if isinstance(value, int | float):
            metrics[str(key)] = float(value)
