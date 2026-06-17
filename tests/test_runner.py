import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from autoresearch_limes.config import ExperimentConfig
from autoresearch_limes.ledger import read_ledger
from autoresearch_limes.runner import run_experiment


class RunnerTests(unittest.TestCase):
    def test_runs_command_captures_metrics_and_appends_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "experiment.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import json
                    print("warmup loss=2.0")
                    print(json.dumps({"metrics": {"val_bpb": 1.234, "loss": 1.5}}))
                    """
                ),
                encoding="utf-8",
            )
            ledger = Path(tmp) / "ledger.jsonl"
            config = ExperimentConfig(
                name="mock",
                command=[sys.executable, str(script)],
                metric_keys=["val_bpb", "loss"],
                timeout_seconds=10,
            )

            result = run_experiment(config, ledger)
            records = read_ledger(ledger)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.metrics["val_bpb"], 1.234)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["metrics"]["loss"], 1.5)
        json.dumps(records[0])


if __name__ == "__main__":
    unittest.main()
