from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ledger import read_ledger
from .spec import ResearchSpec


STATUS_LABELS = {"candidate", "negative", "mixed", "diagnostic", "verified"}


def load_result_artifact(path: str | Path) -> dict[str, Any]:
    artifact_path = Path(path)
    if artifact_path.suffix == ".jsonl":
        records = read_ledger(artifact_path)
        if not records:
            raise ValueError(f"No records found in {artifact_path}")
        return records[-1]

    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        if not data:
            raise ValueError(f"No records found in {artifact_path}")
        data = data[-1]
    if not isinstance(data, dict):
        raise ValueError("Result artifact must be a JSON object, JSON list, or JSONL ledger")
    return data


def generate_result_card(
    record: dict[str, Any],
    output_path: str | Path | None = None,
    spec: ResearchSpec | None = None,
) -> str:
    label = str(record.get("result_label") or record.get("label") or "candidate")
    if label not in STATUS_LABELS:
        raise ValueError(f"unknown result status label: {label}")

    experiment = str(record.get("experiment") or "unnamed-experiment")
    metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
    promotion_gate = (
        _gate_from_spec(record, spec) if spec is not None else record.get("promotion_gate")
    )
    backend = record.get("backend") if isinstance(record.get("backend"), dict) else {}

    lines = [
        f"# {experiment}",
        "",
        f"Status label: {label}",
        f"Run status: {record.get('status', 'unknown')}",
    ]
    if spec is not None:
        lines.append(f"Research objective: {spec.objective}")
        lines.append(f"Expected artifact: {spec.expected_artifact}")
    if "duration_seconds" in record:
        lines.append(f"Duration seconds: {record['duration_seconds']}")
    if backend.get("preferred"):
        lines.append(f"Backend: {backend['preferred']}")
    if record.get("artifact"):
        lines.append(f"Artifact: {record['artifact']}")

    lines.extend(["", "## Metrics", "", "| Metric | Value |", "| --- | ---: |"])
    if metrics:
        for key in sorted(metrics):
            lines.append(f"| {key} | {metrics[key]} |")
    else:
        lines.append("| none | n/a |")

    lines.extend(["", "## Promotion Gate", ""])
    lines.append(_format_gate(promotion_gate))
    lines.extend(["", "## Notes", "", "- Keep negative and diagnostic outcomes in the ledger."])
    card = "\n".join(lines) + "\n"

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(card, encoding="utf-8")
    return card


def _format_gate(value: Any) -> str:
    if not isinstance(value, dict):
        return "Gate: not recorded"

    passed = value.get("passed")
    if passed is True:
        status = "passed"
    elif passed is False:
        status = "not passed"
    else:
        status = "not evaluated"

    metric = value.get("metric", "unknown metric")
    direction = value.get("direction", "unknown direction")
    threshold = value.get("threshold", "unknown threshold")
    return f"Gate: {status} ({metric} {direction} threshold {threshold})"


def _gate_from_spec(record: dict[str, Any], spec: ResearchSpec) -> dict[str, Any]:
    gate = spec.promotion_gate
    metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
    value = metrics.get(gate.metric)
    passed = None
    if isinstance(value, int | float):
        if gate.direction == "higher":
            passed = float(value) >= gate.threshold
        else:
            passed = float(value) <= gate.threshold

    return {
        "metric": gate.metric,
        "direction": gate.direction,
        "threshold": gate.threshold,
        "passed": passed,
    }
