import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.report import generate_result_card
from autoresearch_limes.spec import load_research_spec


class ReportGenerationTests(unittest.TestCase):
    def test_generates_markdown_result_card_from_ledger_record(self) -> None:
        record = {
            "experiment": "nanogpt-grpo-smoke",
            "status": "success",
            "result_label": "mixed",
            "metrics": {"val_loss": 2.4, "val_bpb": 1.12},
            "duration_seconds": 12.5,
            "backend": {"preferred": "cpu"},
            "promotion_gate": {
                "metric": "val_loss",
                "direction": "lower",
                "threshold": 2.25,
                "passed": False,
            },
            "artifact": "runs/nanogpt-grpo-smoke.json",
        }

        card = generate_result_card(record)

        self.assertIn("# nanogpt-grpo-smoke", card)
        self.assertIn("Status label: mixed", card)
        self.assertIn("| val_loss | 2.4 |", card)
        self.assertIn("Gate: not passed", card)
        self.assertIn("runs/nanogpt-grpo-smoke.json", card)

    def test_rejects_unknown_status_label(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown"):
            generate_result_card(
                {
                    "experiment": "bad",
                    "status": "success",
                    "result_label": "spectacular",
                    "metrics": {},
                }
            )

    def test_writes_card_when_output_path_is_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "card.md"

            written = generate_result_card(
                {
                    "experiment": "eurobench-smoke",
                    "status": "success",
                    "metrics": {"score": 0.62},
                },
                output_path=out,
            )

            self.assertEqual(written, out.read_text(encoding="utf-8"))

    def test_uses_spec_to_evaluate_promotion_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(
                """
                {
                  "id": "eurobench-eu-law",
                  "objective": "Check whether a prompt improves EU law scoring.",
                  "hypothesis": "The citation-first prompt improves score.",
                  "method": "Run the fixed EuroBench dev subset.",
                  "baselines": ["current-prompt"],
                  "metrics": [{"name": "score", "direction": "higher", "primary": true}],
                  "costs": {"max_runtime_minutes": 10},
                  "data_boundaries": {
                    "train": "prompt examples",
                    "validation": "public dev tasks",
                    "heldout": "locked final tasks"
                  },
                  "promotion_gate": {
                    "metric": "score",
                    "threshold": 0.7,
                    "direction": "higher"
                  },
                  "expected_artifact": "reports/eurobench-eu-law.md"
                }
                """,
                encoding="utf-8",
            )
            spec = load_research_spec(spec_path)

            card = generate_result_card(
                {
                    "experiment": "eurobench-eu-law",
                    "status": "success",
                    "metrics": {"score": 0.72},
                },
                spec=spec,
            )

        self.assertIn("Research objective: Check whether a prompt improves EU law scoring.", card)
        self.assertIn("Expected artifact: reports/eurobench-eu-law.md", card)
        self.assertIn("Gate: passed (score higher threshold 0.7)", card)

    def test_spec_gate_fails_when_metric_misses_lower_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(
                """
                {
                  "objective": "Lower validation loss.",
                  "hypothesis": "The candidate lowers loss.",
                  "method": "Run a fixed nanoGPT smoke config.",
                  "baselines": ["baseline-config"],
                  "metrics": [{"name": "val_loss", "direction": "lower", "primary": true}],
                  "costs": {"max_runtime_minutes": 10},
                  "data_boundaries": {
                    "train": "training shards",
                    "validation": "validation shards",
                    "heldout": "locked heldout shards"
                  },
                  "promotion_gate": {
                    "metric": "val_loss",
                    "threshold": 2.2,
                    "direction": "lower"
                  },
                  "expected_artifact": "reports/nanogpt-loss.md"
                }
                """,
                encoding="utf-8",
            )
            spec = load_research_spec(spec_path)

            card = generate_result_card(
                {
                    "experiment": "nanogpt-loss",
                    "status": "success",
                    "metrics": {"val_loss": 2.4},
                },
                spec=spec,
            )

        self.assertIn("Gate: not passed (val_loss lower threshold 2.2)", card)


if __name__ == "__main__":
    unittest.main()
