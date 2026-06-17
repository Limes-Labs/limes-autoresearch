import json
import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.config import load_config


class ConfigLoadingTests(unittest.TestCase):
    def test_loads_json_experiment_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "experiment.json"
            path.write_text(
                json.dumps(
                    {
                        "name": "mock",
                        "command": ["python", "examples/mock_experiment.py"],
                        "metric_keys": ["val_bpb", "loss"],
                        "timeout_seconds": 30,
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertEqual(config.name, "mock")
        self.assertEqual(config.command, ["python", "examples/mock_experiment.py"])
        self.assertEqual(config.metric_keys, ["val_bpb", "loss"])
        self.assertEqual(config.timeout_seconds, 30)

    def test_rejects_config_without_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "experiment.json"
            path.write_text(json.dumps({"name": "broken"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
