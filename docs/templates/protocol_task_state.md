# Protocol Task State Template

Use this when an experiment becomes a multi-iteration research loop rather than a single run.

## Directory Shape

```text
task/
  state/
    task_spec.md
    progress.json
    findings.jsonl
    directions_tried.json
    iteration_log.jsonl
  logs/
    work.jsonl
    orchestrator.jsonl
    heartbeat.jsonl
```

## Progress Rules

- Each iteration must name a direction.
- A direction can be used once.
- Findings are append-only.
- An iteration with no findings is stale.
- An iteration where the primary metric regresses is stale.
- One stale iteration is `stalled`.
- Two stale iterations are `pivot-required`.
- Four stale iterations are `needs-human-attention`.

## Heartbeat And Patrol

- `heartbeat TASK --source NAME` updates `state/heartbeat.json` and appends `logs/heartbeat.jsonl`.
- `task-status TASK` reports progress age, heartbeat age, stall state, and recommended action.
- `patrol-tasks ROOT` scans for `state/progress.json` files and reports tasks needing attention.
- Guardian actions are limited to `liveness-check`, `nudge`, and `restart`.
- Patrol may append heartbeat log observations, but it must not edit task progress, findings, or directions.

## Pivot Guidance

When status becomes `pivot-required`, change a structural constraint before continuing. Examples:

- change the split or task family being diagnosed;
- add a missing baseline or control;
- inspect a failure mode instead of tuning the same parameter;
- move from prompt tweaks to data, scoring, or harness checks.

## Current Scope

The CLI initializes and updates the files. It does not run an autonomous watchdog or spawn agents. Future tooling can call `patrol-tasks` on a schedule without relying on chat history.
