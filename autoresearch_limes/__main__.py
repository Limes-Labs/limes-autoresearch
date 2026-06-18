from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import build_adapter_config
from .backends import detect_backends
from .config import load_config
from .ledger import read_ledger
from .protocol import (
    init_protocol_task,
    inspect_protocol_task,
    patrol_protocol_tasks,
    record_iteration,
    touch_heartbeat,
)
from .report import generate_result_card, load_result_artifact
from .runner import run_experiment
from .spec import load_research_spec


def main() -> int:
    parser = argparse.ArgumentParser(prog="autoresearch-limes")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment config")
    run_parser.add_argument("config", type=Path)
    run_parser.add_argument("--ledger", type=Path, default=Path("runs/ledger.jsonl"))

    subparsers.add_parser("detect-backends", help="Print optional backend detection")

    ledger_parser = subparsers.add_parser("ledger", help="Print ledger records")
    ledger_parser.add_argument("--ledger", type=Path, default=Path("runs/ledger.jsonl"))

    spec_parser = subparsers.add_parser("validate-spec", help="Validate a research spec")
    spec_parser.add_argument("spec", type=Path)

    adapter_parser = subparsers.add_parser(
        "adapter-template", help="Print a lightweight Limes repo experiment config"
    )
    adapter_parser.add_argument("adapter")
    adapter_parser.add_argument("--experiment", default="smoke")

    report_parser = subparsers.add_parser(
        "report-card", help="Generate a markdown result card from a result artifact"
    )
    report_parser.add_argument("artifact", type=Path)
    report_parser.add_argument("--spec", type=Path)
    report_parser.add_argument("--out", type=Path)

    init_task_parser = subparsers.add_parser(
        "init-task", help="Initialize persistent protocol state for a research spec"
    )
    init_task_parser.add_argument("spec", type=Path)
    init_task_parser.add_argument("--task-dir", type=Path, required=True)

    record_parser = subparsers.add_parser(
        "record-iteration", help="Append an iteration to a protocol task"
    )
    record_parser.add_argument("task_dir", type=Path)
    record_parser.add_argument("--direction", required=True)
    record_parser.add_argument("--finding", action="append", default=[])
    record_parser.add_argument("--metric", action="append", default=[])

    heartbeat_parser = subparsers.add_parser(
        "heartbeat", help="Update a protocol task heartbeat"
    )
    heartbeat_parser.add_argument("task_dir", type=Path)
    heartbeat_parser.add_argument("--source", default="heartbeat")

    status_parser = subparsers.add_parser(
        "task-status", help="Inspect protocol task liveness and stall state"
    )
    status_parser.add_argument("task_dir", type=Path)
    status_parser.add_argument("--stale-after-seconds", type=float, default=7200)

    patrol_parser = subparsers.add_parser(
        "patrol-tasks", help="Inspect all protocol tasks under a directory"
    )
    patrol_parser.add_argument("root_dir", type=Path)
    patrol_parser.add_argument("--stale-after-seconds", type=float, default=7200)

    args = parser.parse_args()

    if args.command_name == "detect-backends":
        print(json.dumps(detect_backends().to_dict(), indent=2, sort_keys=True))
        return 0

    if args.command_name == "ledger":
        print(json.dumps(read_ledger(args.ledger), indent=2, sort_keys=True))
        return 0

    if args.command_name == "validate-spec":
        spec = load_research_spec(args.spec)
        print(json.dumps(spec.summary(), indent=2, sort_keys=True))
        return 0

    if args.command_name == "adapter-template":
        config = build_adapter_config(args.adapter, args.experiment)
        print(json.dumps(config, indent=2, sort_keys=True))
        return 0

    if args.command_name == "report-card":
        record = load_result_artifact(args.artifact)
        spec = load_research_spec(args.spec) if args.spec is not None else None
        card = generate_result_card(record, args.out, spec=spec)
        print(str(args.out) if args.out is not None else card)
        return 0

    if args.command_name == "init-task":
        progress = init_protocol_task(load_research_spec(args.spec), args.task_dir)
        print(json.dumps(progress, indent=2, sort_keys=True))
        return 0

    if args.command_name == "record-iteration":
        progress = record_iteration(
            args.task_dir,
            direction=args.direction,
            findings=args.finding,
            metrics=_parse_metric_args(args.metric),
        )
        print(json.dumps(progress, indent=2, sort_keys=True))
        return 0

    if args.command_name == "heartbeat":
        heartbeat = touch_heartbeat(args.task_dir, source=args.source)
        print(json.dumps(heartbeat, indent=2, sort_keys=True))
        return 0

    if args.command_name == "task-status":
        status = inspect_protocol_task(
            args.task_dir, stale_after_seconds=args.stale_after_seconds
        )
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0

    if args.command_name == "patrol-tasks":
        report = patrol_protocol_tasks(
            args.root_dir, stale_after_seconds=args.stale_after_seconds
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    if args.command_name == "run":
        result = run_experiment(load_config(args.config), args.ledger)
        print(
            json.dumps(
                {
                    "experiment": result.experiment,
                    "status": result.status,
                    "returncode": result.returncode,
                    "metrics": result.metrics,
                    "ledger": str(args.ledger),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if result.status == "success" else 1

    raise AssertionError(f"Unhandled command: {args.command_name}")


def _parse_metric_args(values: list[str]) -> dict[str, float]:
    metrics = {}
    for value in values:
        key, separator, raw = value.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"Metric must be key=value: {value}")
        metrics[key.strip()] = float(raw)
    return metrics


if __name__ == "__main__":
    raise SystemExit(main())
