# Research Agenda

Limes AutoResearch is intended to become a common ledger and runner layer for Limes experiments, not a single monolithic training repo.

## Near-Term Tracks

### limes-nanogpt

Use the scaffold to wrap small nanoGPT-style experiments:

- fixed wall-clock budgets,
- `val_bpb` or validation loss as primary metrics,
- small model and tokenizer settings for local Mac iteration,
- replay of promising changes on larger hardware.
- explicit train/validation/heldout split descriptions before PPO, GRPO, OPD/OPSD, optimizer, or auxiliary-head claims.

The Karpathy pattern is useful here because it keeps the mutable target narrow and the evaluation budget fixed.

### EuroBench

Use the same ledger flow for European language and multilingual benchmark tasks:

- each benchmark invocation is an experiment command,
- metrics are parsed into JSONL,
- backend and runtime context are recorded,
- model or prompt changes can be compared over time.
- heldout tasks stay locked until final scoring.

EuroBench runs should include dataset version and language subset in future ledger fields.

### Parameter Golf

Parameter Golf needs careful accounting of score, size, and constraints. The runner can already capture scalar metrics; the next step is a benchmark-specific schema for:

- parameter count,
- compressed size,
- score,
- disqualification reason,
- replay command.
- negative and diagnostic labels for ideas that improve one constraint while failing another.

### PPO And GRPO Experiments

The current runner is not an RL training system, but it can record traces needed by one. A future PPO or GRPO planner can treat each experiment as an action and the metric delta as reward.

The design should stay conservative:

- start with bounded search spaces,
- compare against classical HPO baselines,
- record failed and timed-out trials,
- avoid using chat memory as the only optimization state.
- charge critic, teacher, selector, and distillation costs when comparing PPO, GRPO, and OPD/OPSD-style methods.

## Coordination Layer v0.2

AutoResearch now has the minimum pieces needed to coordinate Limes experiments:

- research-question specs in `docs/templates/research_question_spec.json`;
- public no-cheating protocol templates in `docs/templates/no_cheating_protocol.md`;
- adapter command templates for EuroBench, Parameter Golf, and nanoGPT;
- markdown result cards with `candidate`, `negative`, `mixed`, `diagnostic`, and `verified` labels;
- protocol task state with direction tracking, stall detection, heartbeats, and patrol reports;
- a repo-local `limes-autoresearch` Codex skill template for the workflow.

## Lessons From Related Work

- AutoResearch-RL frames the loop as an RL agent editing code and receiving validation reward, but the arXiv entry is currently withdrawn, so it should be treated as context rather than a stable authority.
- Bilevel Autoresearch motivates an outer loop that improves the search mechanism itself. For Limes, this suggests keeping planner prompts, policies, and ledgers versioned.
- AutoResearch-HPO is a useful warning that classical HPO methods can beat pure LLM agents in constrained spaces. Limes should benchmark LLM planners against CMA-ES, TPE, random search, and hybrid policies before trusting them.

## Open Questions

- What is the first Limes benchmark that should become the canonical smoke-plus-real workflow?
- Which metric should be mandatory across ledgers: `val_bpb`, validation loss, benchmark score, or task-specific primary metric?
- How much of the planner state should live in code, prompts, ledgers, or optimizer objects?
- Should the first MLX integration be a native benchmark or a compatibility wrapper around an existing training script?
