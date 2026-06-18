import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.report import generate_result_card


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


if __name__ == "__main__":
    unittest.main()
