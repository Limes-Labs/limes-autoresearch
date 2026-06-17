# Architecture

Limes AutoResearch separates the research loop into stable pieces so experiments can be replayed and audited.

## Components

### Planner

The planner is not implemented as an autonomous agent in this initial scaffold. It is a role boundary: a human, Codex thread, future policy, or HPO process proposes a concrete experiment config and code change. The planner should emit small, reviewable changes and name the expected metric.

### Experiment Runner

`autoresearch_limes.runner.run_experiment` executes one configured command with an optional timeout. It captures stdout and stderr, returns a structured result, and appends a JSONL ledger record.

The runner is deliberately general. It can wrap:

- a mock smoke experiment,
- a nanoGPT training script,
- a Parameter Golf benchmark,
- a EuroBench evaluation command,
- a future MLX or PyTorch training harness.

### Evaluator

`autoresearch_limes.ledger.parse_metrics` extracts metrics from command output. It supports:

- key-value lines, for example `val_bpb=1.42 loss=2.0`;
- JSON lines with a `metrics` object;
- an allowlist of metric keys from the config.

The evaluator does not decide whether a result should be kept. That decision belongs to the planner or a later policy layer.

### Ledger

The ledger is append-only JSONL. Each record includes:

- timestamp,
- experiment name,
- command,
- status,
- return code,
- parsed metrics,
- duration,
- detected backend context.

This makes overnight runs inspectable without assuming a database. A future service can ingest the JSONL into SQLite, Postgres, DuckDB, or a dashboard without changing the local loop.

### Backends

`autoresearch_limes.backends.detect_backends` checks optional runtime support without requiring ML dependencies:

1. PyTorch CUDA, if installed and available.
2. MLX, if installed.
3. PyTorch MPS, if installed and available.
4. CPU fallback.

The detector records context; it does not force the experiment command to use a backend. Benchmark harnesses remain responsible for their own device selection.

## Design Principles

- Keep the harness fixed when comparing experiment changes.
- Keep each experiment small enough to review.
- Prefer explicit ledgers over implicit chat history.
- Treat Mac local runs as first-class smoke and iteration loops.
- Make MLX optional, not a dependency tax for every contributor.
- Avoid claims of autonomous discovery until repeated, replayed benchmarks justify them.

## Future Layers

- A planner adapter that writes candidate configs from a queue.
- A keep/revert policy that compares against a named baseline metric.
- A replay command that reruns the current best on a clean checkout.
- Richer ledgers with git commit, diff summary, seed, dataset, and benchmark version.
- HPO integration where CMA-ES, TPE, or hybrid LLM policies propose bounded parameter changes.
