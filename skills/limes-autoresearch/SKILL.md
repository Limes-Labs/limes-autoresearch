---
name: limes-autoresearch
description: Use when coordinating Limes Labs research experiments with limes-autoresearch: writing or validating research specs, creating lightweight repo adapter configs, initializing protocol task state, recording iterations, checking heartbeat/patrol status, and generating result cards for PPO/GRPO/OPD, EuroBench, Parameter Golf, nanoGPT, or similar reproducible research workflows.
---

# Limes AutoResearch

Use this skill to turn a research idea into a reviewable Limes experiment with an explicit spec, bounded run command, durable protocol state, and markdown result card.

## Workflow

1. Start from a research spec.
   - Use `docs/templates/research_question_spec.json` for new specs.
   - Validate with:
     ```bash
     python3 -m autoresearch_limes validate-spec path/to/spec.json
     ```

2. Create or adapt the run config.
   - For Limes repos, generate a command template:
     ```bash
     python3 -m autoresearch_limes adapter-template eurobench --experiment <name>
     python3 -m autoresearch_limes adapter-template limes-parameter-golf --experiment <name>
     python3 -m autoresearch_limes adapter-template limes-nanogpt --experiment <name>
     ```
   - Replace TODO placeholders before running real experiments.

3. Initialize protocol state for multi-iteration work.
   ```bash
   python3 -m autoresearch_limes init-task path/to/spec.json --task-dir runs/tasks/<task-id>
   ```

4. Run the bounded experiment.
   ```bash
   python3 -m autoresearch_limes run path/to/config.json --ledger runs/<task-id>.jsonl
   ```

5. Record the iteration if work continues.
   ```bash
   python3 -m autoresearch_limes record-iteration runs/tasks/<task-id> \
     --direction "<new direction>" \
     --finding "<verifiable finding>" \
     --metric primary_metric=0.0
   ```

6. Check liveness and stalls.
   ```bash
   python3 -m autoresearch_limes heartbeat runs/tasks/<task-id> --source codex
   python3 -m autoresearch_limes task-status runs/tasks/<task-id>
   python3 -m autoresearch_limes patrol-tasks runs/tasks
   ```

7. Generate the result card.
   ```bash
   python3 -m autoresearch_limes report-card runs/<task-id>.jsonl \
     --spec path/to/spec.json \
     --out reports/<task-id>.md
   ```

## Protocol Rules

- Keep train, validation, and heldout boundaries explicit before running.
- Preserve negative, mixed, diagnostic, failed, and timed-out outcomes.
- Use a new direction for each iteration; repeated directions are rejected.
- Treat one stale iteration as a warning and two stale iterations as a structural-pivot request.
- Patrol may report `liveness-check`, `nudge`, or `restart`, but it must not edit task progress, findings, or directions.
- Do not claim `verified` unless the run was replayed under the locked protocol and passed the promotion gate.

## Current Boundary

This repo provides protocol state, heartbeat/status inspection, adapter templates, and result cards. It does not launch unattended agents or autonomous watchdogs. If the user asks for those, implement them as explicit opt-in automation with tests and clear logs.
