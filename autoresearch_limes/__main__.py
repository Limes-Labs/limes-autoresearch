from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backends import detect_backends
from .config import load_config
from .ledger import read_ledger
from .runner import run_experiment


def main() -> int:
    parser = argparse.ArgumentParser(prog="autoresearch-limes")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment config")
    run_parser.add_argument("config", type=Path)
    run_parser.add_argument("--ledger", type=Path, default=Path("runs/ledger.jsonl"))

    subparsers.add_parser("detect-backends", help="Print optional backend detection")

    ledger_parser = subparsers.add_parser("ledger", help="Print ledger records")
    ledger_parser.add_argument("--ledger", type=Path, default=Path("runs/ledger.jsonl"))

    args = parser.parse_args()

    if args.command_name == "detect-backends":
        print(json.dumps(detect_backends().to_dict(), indent=2, sort_keys=True))
        return 0

    if args.command_name == "ledger":
        print(json.dumps(read_ledger(args.ledger), indent=2, sort_keys=True))
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


if __name__ == "__main__":
    raise SystemExit(main())
