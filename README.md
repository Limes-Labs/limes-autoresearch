# Limes AutoResearch

Limes AutoResearch is a small, runnable scaffold for fixed-budget research loops at Limes Labs. It takes the useful operating pattern from Karpathy-style AutoResearch - propose a change, run a bounded experiment, parse a scalar metric, and append the result to a ledger - and adapts it into a clean project shape for Limes research workflows.

This repository does not claim to autonomously discover frontier architectures. The first goal is humbler and more useful: make experiment loops reviewable, comparable, repeatable, and easy to run on a laptop before pointing them at larger Limes benchmarks.

## What Is Here

- `autoresearch_limes/` - dependency-free runner, config loader, backend detector, and JSONL ledger helpers.
- `examples/` - a tiny mock experiment that runs without GPU dependencies.
- `docs/templates/` - public research-question, no-cheating, and result-artifact templates.
- `tests/` - unit coverage for config loading, metric parsing, backend detection, and runner behavior.
- `docs/architecture.md` - planner, experiment runner, evaluator, ledger, and backend boundaries.
- `docs/research-agenda.md` - how this connects to Limes research tracks such as nanoGPT, EuroBench, Parameter Golf, PPO, and GRPO.
- `UPSTREAMS.md` - upstream repositories inspected, license findings, SHAs, and reuse scope.

## Quickstart

Use Python 3.11 or newer.

```bash
git clone https://github.com/Limes-Labs/limes-autoresearch.git
cd limes-autoresearch

python3 -m unittest discover -s tests
python3 -m autoresearch_limes detect-backends
python3 -m autoresearch_limes run examples/mock_config.json --ledger runs/ledger.jsonl
python3 -m autoresearch_limes ledger --ledger runs/ledger.jsonl
python3 -m autoresearch_limes report-card runs/ledger.jsonl --out runs/mock-result-card.md
```

The smoke experiment prints simple metrics, the runner captures them, and the ledger appends a JSONL record under `runs/ledger.jsonl`.

## Experiment Config

Configs can be JSON or TOML. The minimal shape is:

```json
{
  "name": "mock-smoke",
  "command": ["python3", "examples/mock_experiment.py"],
  "metric_keys": ["val_bpb", "loss"],
  "timeout_seconds": 30
}
```

The runner parses metrics from either key-value output such as `val_bpb=1.23` or JSON output such as:

```json
{"metrics": {"val_bpb": 1.23, "loss": 1.5}}
```

## Backend Detection

Backend detection is optional and graceful. The runner records what it can see:

- CUDA through PyTorch, if `torch` is installed and CUDA is available.
- MLX, if the `mlx` package is installed.
- MPS through PyTorch, if `torch` is installed and Apple Metal is available.
- CPU fallback everywhere else.

No ML framework is required for the default smoke test.

## Limes Usage Pattern

1. Keep the benchmark harness fixed.
2. Let agents or humans propose one experiment change at a time.
3. Run each change under a bounded wall-clock budget.
4. Parse one or more agreed metrics.
5. Append immutable ledger records.
6. Promote only changes that survive replay and review.

That pattern is intentionally compatible with Limes nanoGPT experiments, Apple Silicon local trials, optional MLX ports, and later PPO/GRPO-based proposal policies.

## Research Workflow

Start by writing a research-question spec. The schema is intentionally explicit about the scientific boundary of the run: objective, hypothesis, method, baselines, metrics, costs, train/validation/heldout splits, promotion gate, and expected artifact.

```bash
python3 -m autoresearch_limes validate-spec examples/ppo_grpo_research_spec.json
```

Use `docs/templates/no_cheating_protocol.md` when opening a public experiment issue or PR. The template asks contributors to freeze the metric, name data boundaries, account for compute and teacher/critic/selector costs, and keep negative or diagnostic runs in the ledger.

For existing Limes repos, generate a lightweight command template and then replace the TODO placeholders with the real repo command:

```bash
python3 -m autoresearch_limes adapter-template eurobench --experiment eu-law-v04
python3 -m autoresearch_limes adapter-template limes-parameter-golf --experiment tiny-transformer
python3 -m autoresearch_limes adapter-template limes-nanogpt --experiment grpo-smoke
```

After a run, turn the JSONL ledger or a JSON result artifact into a markdown result card:

```bash
python3 -m autoresearch_limes report-card runs/ledger.jsonl --out reports/my-result-card.md
```

Result cards use the status labels `candidate`, `negative`, `mixed`, `diagnostic`, and `verified`. `verified` should be reserved for replayed runs that satisfy the locked promotion gate.

### Example: PPO/GRPO Toy Study

1. Copy `examples/ppo_grpo_research_spec.json` and update the split descriptions, cost cap, and promotion threshold.
2. Validate the spec with `validate-spec`.
3. Generate a repo adapter if the run targets EuroBench, Parameter Golf, or nanoGPT, or write a normal experiment config for a toy PPO/GRPO command.
4. Run the experiment into a JSONL ledger.
5. Generate a result card and publish the spec, ledger snippet, and card together.

## Attribution

See `UPSTREAMS.md`. This initial implementation is original Limes code. It reuses concepts and operating patterns from the inspected repositories, not source code.
