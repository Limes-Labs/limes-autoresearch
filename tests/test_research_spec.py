import json
import tempfile
import unittest
from pathlib import Path

from autoresearch_limes.spec import load_research_spec


class ResearchSpecTests(unittest.TestCase):
    def test_loads_complete_research_question_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ppo_vs_grpo.json"
            path.write_text(
                json.dumps(
                    {
                        "id": "ppo-grpo-credit-assignment-smoke",
                        "objective": "Compare credit assignment on variable-length toy traces.",
                        "hypothesis": "Critic-style advantages improve heldout reward.",
                        "method": "Run matched PPO-style and group-relative baselines.",
                        "baselines": ["random-policy", "grpo-group-mean"],
                        "metrics": [
                            {
                                "name": "heldout_reward",
                                "direction": "higher",
                                "primary": True,
                            }
                        ],
                        "costs": {
                            "max_runtime_minutes": 30,
                            "max_budget_eur": 2.5,
                            "hardware": "cpu",
                        },
                        "data_boundaries": {
                            "train": "toy traces seeds 1-20",
                            "validation": "toy traces seeds 21-25",
                            "heldout": "toy traces seeds 100-110",
                        },
                        "promotion_gate": {
                            "metric": "heldout_reward",
                            "threshold": 0.03,
                            "direction": "higher",
                            "requires_replay": True,
                        },
                        "expected_artifact": "reports/ppo_grpo_credit_assignment.md",
                    }
                ),
                encoding="utf-8",
            )

            spec = load_research_spec(path)

        self.assertEqual(spec.identifier, "ppo-grpo-credit-assignment-smoke")
        self.assertEqual(spec.primary_metric.name, "heldout_reward")
        self.assertEqual(spec.data_boundaries.heldout, "toy traces seeds 100-110")
        self.assertTrue(spec.promotion_gate.requires_replay)

    def test_rejects_spec_without_heldout_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(
                json.dumps(
                    {
                        "objective": "Measure a candidate.",
                        "hypothesis": "Candidate improves score.",
                        "method": "Run a benchmark.",
                        "baselines": ["baseline"],
                        "metrics": [{"name": "score", "direction": "higher"}],
                        "costs": {"max_runtime_minutes": 5},
                        "data_boundaries": {
                            "train": "train split",
                            "validation": "validation split",
                        },
                        "promotion_gate": {
                            "metric": "score",
                            "threshold": 0.01,
                            "direction": "higher",
                        },
                        "expected_artifact": "reports/result.md",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "heldout"):
                load_research_spec(path)


if __name__ == "__main__":
    unittest.main()
