import json
import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.protocol import init_protocol_task, record_iteration
from autoresearch_limes.spec import load_research_spec


class ProtocolStateTests(unittest.TestCase):
    def test_initializes_task_state_from_research_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = load_research_spec(_write_spec(Path(tmp)))
            task_dir = Path(tmp) / "tasks" / spec.identifier

            progress = init_protocol_task(spec, task_dir)

            self.assertEqual(progress["experiment"], "loop-smoke")
            self.assertEqual(progress["iteration"], 0)
            self.assertEqual(progress["status"], "active")
            self.assertEqual(progress["stale_count"], 0)
            self.assertTrue((task_dir / "state" / "task_spec.md").exists())
            self.assertTrue((task_dir / "state" / "findings.jsonl").exists())
            self.assertTrue((task_dir / "state" / "directions_tried.json").exists())
            self.assertTrue((task_dir / "logs" / "work.jsonl").exists())
            self.assertTrue((task_dir / "logs" / "orchestrator.jsonl").exists())

    def test_records_iteration_and_rejects_repeated_direction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = load_research_spec(_write_spec(Path(tmp)))
            task_dir = Path(tmp) / "task"
            init_protocol_task(spec, task_dir)

            progress = record_iteration(
                task_dir,
                direction="try citation-first prompt",
                findings=["score improves on public dev"],
                metrics={"score": 0.72},
            )

            self.assertEqual(progress["iteration"], 1)
            self.assertEqual(progress["total_findings"], 1)
            self.assertEqual(progress["stale_count"], 0)
            self.assertEqual(progress["last_metric"], 0.72)
            self.assertEqual(json.loads((task_dir / "state" / "directions_tried.json").read_text()), [
                "try citation-first prompt"
            ])

            with self.assertRaisesRegex(ValueError, "direction"):
                record_iteration(
                    task_dir,
                    direction="try citation-first prompt",
                    findings=["same direction again"],
                    metrics={"score": 0.74},
                )

    def test_stale_iterations_trigger_structural_pivot_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = load_research_spec(_write_spec(Path(tmp)))
            task_dir = Path(tmp) / "task"
            init_protocol_task(spec, task_dir)
            record_iteration(
                task_dir,
                direction="baseline prompt",
                findings=["baseline established"],
                metrics={"score": 0.72},
            )

            first_stale = record_iteration(
                task_dir,
                direction="minor wording tweak",
                findings=[],
                metrics={"score": 0.70},
            )
            second_stale = record_iteration(
                task_dir,
                direction="temperature-only tweak",
                findings=[],
                metrics={"score": 0.68},
            )

            self.assertEqual(first_stale["stale_count"], 1)
            self.assertEqual(first_stale["status"], "stalled")
            self.assertEqual(second_stale["stale_count"], 2)
            self.assertEqual(second_stale["status"], "pivot-required")
            self.assertEqual(
                second_stale["recommended_action"],
                "change a structural constraint before the next iteration",
            )


def _write_spec(root: Path) -> Path:
    path = root / "spec.json"
    path.write_text(
        json.dumps(
            {
                "id": "loop-smoke",
                "objective": "Keep a long-running benchmark loop from stalling.",
                "hypothesis": "Explicit state makes pivots easier to audit.",
                "method": "Run short iterations and record findings.",
                "baselines": ["current loop"],
                "metrics": [{"name": "score", "direction": "higher", "primary": True}],
                "costs": {"max_runtime_minutes": 30},
                "data_boundaries": {
                    "train": "prompt examples",
                    "validation": "public dev tasks",
                    "heldout": "locked final tasks",
                },
                "promotion_gate": {
                    "metric": "score",
                    "threshold": 0.8,
                    "direction": "higher",
                },
                "expected_artifact": "reports/loop-smoke.md",
            }
        ),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    unittest.main()
