# Architecture

Limes AutoResearch separates the research loop into stable pieces so experiments can be replayed and audited.

## Components

### Planner

The planner is not implemented as an autonomous agent in this initial scaffold. It is a role boundary: a human, Codex thread, future policy, or HPO process proposes a concrete experiment config and code change. The planner should emit small, reviewable changes and name the expected metric.

`autoresearch_limes.spec.load_research_spec` gives the planner a public contract for research questions. A valid spec includes:

- objective,
- hypothesis,
- method,
- baselines,
- metrics and direction,
- cost limits,
- train/validation/heldout boundaries,
- promotion gate,
- expected artifact.

This keeps PPO/GRPO/OPD paper experiments, nanoGPT trials, Parameter Golf entries, and EuroBench evaluations comparable before they become expensive.

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

### Repo Adapters

`autoresearch_limes.adapters.build_adapter_config` emits lightweight command templates for:

- `eurobench`,
- `limes-parameter-golf`,
- `limes-nanogpt`.

The templates are deliberately shallow. They do not import those repos or require their dependencies. They provide the first config shape a contributor can copy into a checked-out repo and edit into a real command.

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

### Protocol State

`autoresearch_limes.protocol` adds a file-backed state layer for longer loops. It is inspired by Deli_AutoResearch-style protocol scaffolding, but narrowed to what this repo can enforce locally:

- initialize a task directory from a research spec;
- persist `state/progress.json`, `state/directions_tried.json`, `state/findings.jsonl`, and `state/iteration_log.jsonl`;
- create separate `logs/work.jsonl`, `logs/orchestrator.jsonl`, and `logs/heartbeat.jsonl` streams for future tooling;
- reject repeated directions;
- increment `stale_count` when an iteration has no findings or the primary metric regresses;
- request a structural pivot after two stale iterations.
- update task heartbeats;
- inspect one task's liveness;
- patrol a directory of protocol tasks and report which ones need attention.

This layer does not launch unattended agents or watchdogs. It gives humans, Codex threads, and future orchestrators a stable state contract. Patrol output is intentionally read-only with respect to task progress: it may append heartbeat patrol logs, but it does not edit findings, directions, or progress.

### Reports

`autoresearch_limes.report.generate_result_card` converts a ledger record or JSON result artifact into a markdown card. The card records metrics, runtime context, promotion-gate status, and the artifact path. If a research spec is provided, the card includes the objective, expected artifact, and an automatic pass/fail evaluation of the spec's promotion gate.

Status labels are:

- `candidate` - worth replaying or comparing;
- `negative` - did not beat the baseline or failed the gate;
- `mixed` - improved one target while regressing another;
- `diagnostic` - useful for understanding a mechanism, not a claim;
- `verified` - replayed under the locked protocol and passed the gate.

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
- Optional automation hooks that call `patrol-tasks` on a schedule and route attention reports.
- HPO integration where CMA-ES, TPE, or hybrid LLM policies propose bounded parameter changes.
