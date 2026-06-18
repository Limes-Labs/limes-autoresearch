import unittest

from autoresearch_limes.adapters import adapter_names, build_adapter_config


class AdapterTemplateTests(unittest.TestCase):
    def test_exposes_limes_repo_adapters(self) -> None:
        self.assertEqual(
            {"eurobench", "limes-parameter-golf", "limes-nanogpt"},
            set(adapter_names()),
        )

    def test_eurobench_template_records_benchmark_metrics(self) -> None:
        config = build_adapter_config("eurobench", "eu-law-eval")

        self.assertEqual(config["name"], "eurobench-eu-law-eval")
        self.assertIn("score", config["metric_keys"])
        self.assertIn("pass_rate", config["metric_keys"])
        self.assertIn("python", config["command"][0])
        self.assertIn("TODO: replace", config["notes"])

    def test_parameter_golf_template_tracks_cost_and_size(self) -> None:
        config = build_adapter_config("limes-parameter-golf", "tiny-transformer")

        self.assertEqual(config["name"], "parameter-golf-tiny-transformer")
        self.assertIn("compressed_size_bytes", config["metric_keys"])
        self.assertIn("score", config["metric_keys"])

    def test_nanogpt_template_uses_validation_metrics(self) -> None:
        config = build_adapter_config("limes-nanogpt", "grpo-smoke")

        self.assertEqual(config["name"], "nanogpt-grpo-smoke")
        self.assertIn("val_loss", config["metric_keys"])
        self.assertIn("val_bpb", config["metric_keys"])


if __name__ == "__main__":
    unittest.main()
