# Limes AutoResearch Program

This is a lightweight operating protocol for a research agent working in this repository.

## Rules

1. Read `UPSTREAMS.md` before proposing code reuse from external repositories.
2. Keep each experiment change small and reviewable.
3. Run the smoke test before and after runner changes.
4. Record every experiment through the ledger; do not rely on chat history as the source of truth.
5. Prefer local CPU or Mac-friendly smoke tests before GPU-heavy runs.
6. Do not claim autonomous discovery from one-off results.

## Default Loop

1. Inspect the current ledger.
2. Choose one hypothesis.
3. Edit the experiment target or config.
4. Run a bounded experiment.
5. Compare the primary metric against the baseline.
6. Keep, revert, or queue for replay.

The initial repository only implements the runner and ledger. Planner policy, keep/revert automation, and benchmark-specific adapters are future work.
