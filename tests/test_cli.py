import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_validate_spec_command_prints_spec_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(
                json.dumps(
                    {
                        "id": "eurobench-smoke",
                        "objective": "Check an eval harness.",
                        "hypothesis": "The prompt improves score.",
                        "method": "Run fixed EuroBench subset.",
                        "baselines": ["current prompt"],
                        "metrics": [{"name": "score", "direction": "higher"}],
                        "costs": {"max_runtime_minutes": 10},
                        "data_boundaries": {
                            "train": "no training data",
                            "validation": "public dev tasks",
                            "heldout": "private locked tasks",
                        },
                        "promotion_gate": {
                            "metric": "score",
                            "threshold": 0.02,
                            "direction": "higher",
                        },
                        "expected_artifact": "reports/eurobench-smoke.md",
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, "-m", "autoresearch_limes", "validate-spec", str(spec)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["id"], "eurobench-smoke")
        self.assertEqual(payload["primary_metric"], "score")

    def test_adapter_template_command_prints_config(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autoresearch_limes",
                "adapter-template",
                "limes-nanogpt",
                "--experiment",
                "grpo-smoke",
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["name"], "nanogpt-grpo-smoke")
        self.assertIn("val_loss", payload["metric_keys"])

    def test_report_card_command_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            record_path = Path(tmp) / "record.json"
            out = Path(tmp) / "card.md"
            record_path.write_text(
                json.dumps(
                    {
                        "experiment": "parameter-golf-smoke",
                        "status": "success",
                        "result_label": "candidate",
                        "metrics": {"score": 0.5},
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "report-card",
                    str(record_path),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(str(out), completed.stdout.strip())
            self.assertIn("Status label: candidate", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
