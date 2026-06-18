# No-Cheating Protocol Template

## Frozen Question

- Experiment:
- Objective:
- Primary metric:
- Metric direction: higher/lower

## Split Boundaries

- Train/proposal data:
- Validation/selection data:
- Heldout/final data:
- Rule: heldout labels, hidden answers, private benchmark tasks, or final scores may not influence candidate selection.

## Budget Accounting

- Wall-clock budget:
- Token/sample/update budget:
- Hardware budget:
- Extra teacher, critic, selector, retrieval, or preprocessing cost:

## Baselines And Controls

- Primary baseline:
- Candidate:
- Control or ablation:
- Replay requirement:

## Promotion Gate

- Promote only if:
- Mark as `negative` if:
- Mark as `mixed` if:
- Mark as `diagnostic` if:
- Mark as `verified` only after replay on the locked protocol:

## Reporting

- Keep failed, timed-out, negative, and diagnostic runs in the ledger.
- Publish the result card with metric values, costs, split boundaries, gate decision, and artifact path.
