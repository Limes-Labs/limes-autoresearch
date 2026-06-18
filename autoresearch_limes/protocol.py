from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .spec import ResearchSpec


def init_protocol_task(spec: ResearchSpec, task_dir: str | Path) -> dict[str, Any]:
    root = Path(task_dir)
    state_dir = root / "state"
    logs_dir = root / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    progress = {
        "experiment": spec.identifier,
        "iteration": 0,
        "status": "active",
        "stale_count": 0,
        "total_findings": 0,
        "primary_metric": spec.primary_metric.name,
        "metric_direction": spec.primary_metric.direction,
        "last_metric": None,
        "best_metric": None,
        "recommended_action": "run the next bounded iteration",
        "last_seen": _timestamp(),
    }

    _write_json(state_dir / "progress.json", progress)
    _write_json(state_dir / "directions_tried.json", [])
    (state_dir / "findings.jsonl").touch()
    (state_dir / "iteration_log.jsonl").touch()
    (logs_dir / "work.jsonl").touch()
    (logs_dir / "orchestrator.jsonl").touch()
    (logs_dir / "heartbeat.jsonl").touch()
    (state_dir / "task_spec.md").write_text(_task_spec_markdown(spec), encoding="utf-8")

    return progress


def record_iteration(
    task_dir: str | Path,
    *,
    direction: str,
    findings: list[str],
    metrics: dict[str, float],
) -> dict[str, Any]:
    root = Path(task_dir)
    state_dir = root / "state"
    progress_path = state_dir / "progress.json"
    directions_path = state_dir / "directions_tried.json"

    progress = _read_json(progress_path)
    directions = _read_json(directions_path)
    normalized_direction = direction.strip()
    if not normalized_direction:
        raise ValueError("iteration direction cannot be empty")
    if normalized_direction in directions:
        raise ValueError(f"iteration direction already tried: {normalized_direction}")

    metric_name = str(progress["primary_metric"])
    metric_direction = str(progress["metric_direction"])
    metric_value = metrics.get(metric_name)
    stale_reasons = _stale_reasons(
        findings=findings,
        metric_value=metric_value,
        last_metric=progress.get("last_metric"),
        metric_direction=metric_direction,
    )

    iteration = int(progress["iteration"]) + 1
    total_findings = int(progress["total_findings"]) + len(findings)
    stale_count = int(progress["stale_count"]) + 1 if stale_reasons else 0
    status = _status_for_stale_count(stale_count)
    recommended_action = _recommended_action(status)

    directions.append(normalized_direction)
    progress.update(
        {
            "iteration": iteration,
            "status": status,
            "stale_count": stale_count,
            "total_findings": total_findings,
            "last_seen": _timestamp(),
            "recommended_action": recommended_action,
        }
    )
    if isinstance(metric_value, int | float):
        progress["last_metric"] = float(metric_value)
        progress["best_metric"] = _best_metric(
            current=progress.get("best_metric"),
            candidate=float(metric_value),
            direction=metric_direction,
        )

    _write_json(directions_path, directions)
    _write_json(progress_path, progress)
    _append_iteration_log(
        state_dir / "iteration_log.jsonl",
        {
            "ts": _timestamp(),
            "iteration": iteration,
            "direction": normalized_direction,
            "findings_count": len(findings),
            "metrics": metrics,
            "stale_reasons": stale_reasons,
            "status": status,
        },
    )
    for finding in findings:
        _append_iteration_log(
            state_dir / "findings.jsonl",
            {"ts": _timestamp(), "iteration": iteration, "finding": finding},
        )

    return progress


def touch_heartbeat(task_dir: str | Path, source: str = "heartbeat") -> dict[str, Any]:
    root = Path(task_dir)
    payload = {
        "ts": _timestamp(),
        "source": source,
        "event": "heartbeat",
        "guardian_allowed_actions": _guardian_allowed_actions(),
    }
    _write_json(root / "state" / "heartbeat.json", payload)
    _append_iteration_log(root / "logs" / "heartbeat.jsonl", payload)
    return payload


def inspect_protocol_task(
    task_dir: str | Path, stale_after_seconds: float = 7200
) -> dict[str, Any]:
    root = Path(task_dir)
    progress = _read_json(root / "state" / "progress.json")
    heartbeat_path = root / "state" / "heartbeat.json"
    heartbeat = _read_json(heartbeat_path) if heartbeat_path.exists() else None
    progress_age = _age_seconds(progress.get("last_seen"))
    heartbeat_age = _age_seconds(heartbeat.get("ts")) if isinstance(heartbeat, dict) else None
    progress_stale = progress_age is None or progress_age >= stale_after_seconds
    heartbeat_stale = heartbeat_age is None or heartbeat_age >= stale_after_seconds
    task_status = str(progress.get("status", "unknown"))
    needs_attention = (
        progress_stale
        or heartbeat_stale
        or task_status in {"stalled", "pivot-required", "needs-human-attention"}
    )

    return {
        "task_dir": str(root),
        "experiment": progress.get("experiment"),
        "iteration": progress.get("iteration"),
        "status": task_status,
        "stale_count": progress.get("stale_count"),
        "recommended_action": progress.get("recommended_action"),
        "progress_age_seconds": progress_age,
        "heartbeat_age_seconds": heartbeat_age,
        "progress_stale": progress_stale,
        "heartbeat_stale": heartbeat_stale,
        "needs_attention": needs_attention,
        "guardian_allowed_actions": _guardian_allowed_actions(),
    }


def patrol_protocol_tasks(
    root_dir: str | Path, stale_after_seconds: float = 7200
) -> dict[str, Any]:
    root = Path(root_dir)
    task_dirs = sorted({path.parent.parent for path in root.rglob("state/progress.json")})
    statuses = [
        inspect_protocol_task(task_dir, stale_after_seconds=stale_after_seconds)
        for task_dir in task_dirs
    ]
    for status in statuses:
        _append_iteration_log(
            Path(status["task_dir"]) / "logs" / "heartbeat.jsonl",
            {
                "ts": _timestamp(),
                "source": "patrol",
                "event": "patrol",
                "needs_attention": status["needs_attention"],
                "recommended_action": status["recommended_action"],
            },
        )

    attention = [status for status in statuses if status["needs_attention"]]
    return {
        "root_dir": str(root),
        "tasks_checked": len(statuses),
        "attention_needed": len(attention),
        "task_dirs": [status["task_dir"] for status in statuses],
        "attention_task_dirs": [status["task_dir"] for status in attention],
        "tasks": statuses,
    }


def _stale_reasons(
    *,
    findings: list[str],
    metric_value: float | None,
    last_metric: Any,
    metric_direction: str,
) -> list[str]:
    reasons = []
    if not findings:
        reasons.append("no_new_findings")
    if isinstance(metric_value, int | float) and isinstance(last_metric, int | float):
        if metric_direction == "higher" and metric_value < last_metric:
            reasons.append("metric_regression")
        if metric_direction == "lower" and metric_value > last_metric:
            reasons.append("metric_regression")
    return reasons


def _status_for_stale_count(stale_count: int) -> str:
    if stale_count >= 4:
        return "needs-human-attention"
    if stale_count >= 2:
        return "pivot-required"
    if stale_count == 1:
        return "stalled"
    return "active"


def _recommended_action(status: str) -> str:
    if status == "pivot-required":
        return "change a structural constraint before the next iteration"
    if status == "needs-human-attention":
        return "write an escalation report before continuing"
    if status == "stalled":
        return "try a direction that differs from previous attempts"
    return "run the next bounded iteration"


def _best_metric(current: Any, candidate: float, direction: str) -> float:
    if not isinstance(current, int | float):
        return candidate
    if direction == "higher":
        return max(float(current), candidate)
    return min(float(current), candidate)


def _guardian_allowed_actions() -> list[str]:
    return ["liveness-check", "nudge", "restart"]


def _age_seconds(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return (datetime.now(UTC) - timestamp).total_seconds()


def _task_spec_markdown(spec: ResearchSpec) -> str:
    return "\n".join(
        [
            f"# {spec.identifier}",
            "",
            f"Objective: {spec.objective}",
            f"Hypothesis: {spec.hypothesis}",
            f"Method: {spec.method}",
            f"Primary metric: {spec.primary_metric.name} ({spec.primary_metric.direction})",
            f"Expected artifact: {spec.expected_artifact}",
            "",
            "## Baselines",
            *[f"- {baseline}" for baseline in spec.baselines],
            "",
            "## Boundaries",
            f"- Train: {spec.data_boundaries.train}",
            f"- Validation: {spec.data_boundaries.validation}",
            f"- Heldout: {spec.data_boundaries.heldout}",
            "",
        ]
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_iteration_log(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()
