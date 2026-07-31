# P12 Exit Review

- **Milestone:** P12 local model-assisted preview
- **Status:** Implementation candidate, review ready
- **Branch:** `agent/p12-local-model-assisted-preview`
- **Pull request:** #55
- **Baseline:** merged P11 commit `cdd5c3d50c4166ae8f01be2bcee45eb5f411cbb7`
- **Hosted Quality:** Run `30645896227` passed on implementation head `cb3db8c2e6010601f7bedb074a27c9528010b12c`

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

## Automated and hosted validation

Quality run `30645896227` passed:

- Ruff
- strict mypy across 193 source files
- 324 tests, including all seven P12 tests
- contracts, migrations, links, and architecture checks
- OpenSpec doctor and strict validation
- secret scanning

The seven P12 tests cover deterministic inference, input budget rejection, fixture review state, missing-fixture policy block, unavailable live executor, atomic retention, and CLI evidence output.

## Completion decision

REQ-0240 through REQ-0246 are implemented and evidenced for the approved optional P12 scope. P12 remains an implementation candidate until PR #55 is reviewed and merged. P13 remains evidence-gated and is not implied by P12 completion.
