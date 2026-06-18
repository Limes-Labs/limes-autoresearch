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

    def test_report_card_command_can_use_spec_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            record_path = Path(tmp) / "record.json"
            spec_path = Path(tmp) / "spec.json"
            out = Path(tmp) / "card.md"
            record_path.write_text(
                json.dumps(
                    {
                        "experiment": "parameter-golf-smoke",
                        "status": "success",
                        "metrics": {"score": 0.82},
                    }
                ),
                encoding="utf-8",
            )
            spec_path.write_text(
                json.dumps(
                    {
                        "objective": "Test an efficiency candidate.",
                        "hypothesis": "The candidate clears the score floor.",
                        "method": "Run a fixed Parameter Golf benchmark.",
                        "baselines": ["baseline-entry"],
                        "metrics": [{"name": "score", "direction": "higher"}],
                        "costs": {"max_runtime_minutes": 10},
                        "data_boundaries": {
                            "train": "training inputs",
                            "validation": "public validation cases",
                            "heldout": "locked final cases",
                        },
                        "promotion_gate": {
                            "metric": "score",
                            "threshold": 0.8,
                            "direction": "higher",
                        },
                        "expected_artifact": "reports/parameter-golf-smoke.md",
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
                    "--spec",
                    str(spec_path),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Gate: passed", out.read_text(encoding="utf-8"))

    def test_protocol_task_cli_initializes_and_records_iteration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            task_dir = Path(tmp) / "task"
            spec_path.write_text(
                json.dumps(
                    {
                        "id": "cli-loop",
                        "objective": "Track a long-running loop.",
                        "hypothesis": "Persistent state prevents silent stalls.",
                        "method": "Record one iteration at a time.",
                        "baselines": ["manual notes"],
                        "metrics": [{"name": "score", "direction": "higher"}],
                        "costs": {"max_runtime_minutes": 10},
                        "data_boundaries": {
                            "train": "proposal notes",
                            "validation": "dev tasks",
                            "heldout": "locked tasks",
                        },
                        "promotion_gate": {
                            "metric": "score",
                            "threshold": 0.5,
                            "direction": "higher",
                        },
                        "expected_artifact": "reports/cli-loop.md",
                    }
                ),
                encoding="utf-8",
            )

            init_completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "init-task",
                    str(spec_path),
                    "--task-dir",
                    str(task_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            record_completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "record-iteration",
                    str(task_dir),
                    "--direction",
                    "try stricter prompt",
                    "--finding",
                    "score improved on dev",
                    "--metric",
                    "score=0.6",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(init_completed.returncode, 0, init_completed.stderr)
            self.assertEqual(record_completed.returncode, 0, record_completed.stderr)
            payload = json.loads(record_completed.stdout)
            self.assertEqual(payload["iteration"], 1)
            self.assertEqual(payload["status"], "active")

    def test_protocol_status_and_patrol_cli_report_task_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            task_dir = Path(tmp) / "task"
            spec_path.write_text(
                json.dumps(
                    {
                        "id": "cli-patrol",
                        "objective": "Track liveness.",
                        "hypothesis": "Patrol output identifies stale loops.",
                        "method": "Inspect task state.",
                        "baselines": ["manual inspection"],
                        "metrics": [{"name": "score", "direction": "higher"}],
                        "costs": {"max_runtime_minutes": 10},
                        "data_boundaries": {
                            "train": "proposal notes",
                            "validation": "dev tasks",
                            "heldout": "locked tasks",
                        },
                        "promotion_gate": {
                            "metric": "score",
                            "threshold": 0.5,
                            "direction": "higher",
                        },
                        "expected_artifact": "reports/cli-patrol.md",
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "init-task",
                    str(spec_path),
                    "--task-dir",
                    str(task_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            heartbeat_completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "heartbeat",
                    str(task_dir),
                    "--source",
                    "cli-test",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            status_completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "task-status",
                    str(task_dir),
                    "--stale-after-seconds",
                    "0",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            patrol_completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoresearch_limes",
                    "patrol-tasks",
                    str(Path(tmp)),
                    "--stale-after-seconds",
                    "0",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(heartbeat_completed.returncode, 0, heartbeat_completed.stderr)
            self.assertEqual(status_completed.returncode, 0, status_completed.stderr)
            self.assertEqual(patrol_completed.returncode, 0, patrol_completed.stderr)
            self.assertEqual(json.loads(heartbeat_completed.stdout)["source"], "cli-test")
            self.assertTrue(json.loads(status_completed.stdout)["heartbeat_stale"])
            self.assertEqual(json.loads(patrol_completed.stdout)["tasks_checked"], 1)


if __name__ == "__main__":
    unittest.main()
