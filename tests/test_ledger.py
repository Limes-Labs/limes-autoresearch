import json
import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.ledger import parse_metrics, read_ledger, write_ledger_record


class LedgerTests(unittest.TestCase):
    def test_parses_key_value_and_json_metrics(self) -> None:
        output = "\n".join(
            [
                "step=1 loss=2.5",
                '{"metrics": {"val_bpb": 1.75, "accuracy": 0.25}}',
                "final val_bpb=1.5 elapsed_seconds=3",
            ]
        )

        metrics = parse_metrics(output, metric_keys=["val_bpb", "loss"])

        self.assertEqual(metrics["loss"], 2.5)
        self.assertEqual(metrics["val_bpb"], 1.5)
        self.assertNotIn("accuracy", metrics)

    def test_writes_and_reads_jsonl_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"

            write_ledger_record(
                ledger,
                {
                    "experiment": "mock",
                    "status": "success",
                    "metrics": {"val_bpb": 1.25},
                },
            )

            records = read_ledger(ledger)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["experiment"], "mock")
        self.assertEqual(records[0]["metrics"]["val_bpb"], 1.25)
        json.dumps(records[0])


if __name__ == "__main__":
    unittest.main()
