# P12 Exit Review

- **Milestone:** P12 local model-assisted preview
- **Status:** Implementation candidate; hosted Quality and review pending
- **Branch:** `agent/p12-local-model-assisted-preview`
- **Pull request:** pending
- **Baseline:** merged P11 commit `cdd5c3d50c4166ae8f01be2bcee45eb5f411cbb7`

## Implemented evidence

- Immutable preview budget, request, status, review, and evidence contracts.
- Deterministic local ordinary-least-squares trend preview.
- Fixture-backed LLM analysis preview with exact provider/model/prompt identity.
- Explicit `succeeded`, `review_required`, `budget_exceeded`, `policy_blocked`, and `provider_unavailable` outcomes.
- Input digests, model identity, prompt identity, output, metrics, findings, cost, latency, and disabled safety boundaries.
- Atomic local evidence retention and CLI inspection.

## Safety behavior

- Network/model calls are disabled by default.
- No fixture plus no network returns `policy_blocked`.
- Explicit live mode returns `provider_unavailable` because no executor is configured.
- Fixture-backed LLM output always requires human review.
- Recommendations, brokers, autonomous actions, and real-capital orders remain disabled.

## Automated validation

Tests cover:

- deterministic local inference
- local input-budget rejection
- fixture-backed LLM review state
- missing-fixture policy block
- unavailable live executor
- atomic evidence retention
- CLI evidence output

## Hosted validation

Pending:

- Ruff
- strict mypy
- pytest, contracts, migrations, links, and architecture checks
- OpenSpec doctor and strict validation
- secret scanning

## Completion decision

P12 remains an implementation candidate until Quality is green, documentation and traceability are reconciled, the branch diff is reviewed, and the PR is merged.
