# P12 Local Model-Assisted Preview Specification

## Purpose

Turn the M9-M10 ML/LLM governance contracts into optional local previews without introducing a required model provider.

## Requirements

- **REQ-0240:** P12 SHALL provide one deterministic local numeric inference path.
- **REQ-0241:** P12 SHALL provide fixture-backed LLM analysis with exact provider, model, and prompt identity.
- **REQ-0242:** P12 SHALL enforce input, output, cost, and latency budgets before evidence is accepted.
- **REQ-0243:** P12 SHALL retain immutable input digest, model identity, prompt identity, output, metrics, findings, cost, latency, and review status.
- **REQ-0244:** P12 SHALL disable network/model calls by default and fail closed when no fixture is supplied.
- **REQ-0245:** P12 SHALL require human review for every LLM-derived output and SHALL not label it as financial advice.
- **REQ-0246:** P12 SHALL preserve all deferred provider, credential, production-serving, recommendation, broker, autonomous-action, and real-order boundaries.

## Implemented paths

### Deterministic local trend preview

The local preview fits an ordinary-least-squares line to explicit numeric values and emits slope, intercept, mean-squared error, direction, and next-value evidence. It is deterministic, network-disabled, and zero-cost.

### Fixture-backed LLM analysis preview

The LLM preview accepts explicit input text, prompt identity, exact provider/model identity, budgets, and a fixture response. Fixture output is retained as `review_required` with human-review and not-financial-advice findings.

When network access is disabled and no fixture exists, the result is `policy_blocked`. When a caller explicitly checks live mode, the result is `provider_unavailable` until a separately governed executor exists. No credential is resolved and no network call occurs.

## Evidence statuses

- `succeeded`
- `review_required`
- `budget_exceeded`
- `policy_blocked`
- `provider_unavailable`

## Explicit non-scope

- Remote model invocation and credential resolution
- Automatic training, retraining, promotion, or production serving
- Tool execution or state mutation
- Authoritative recommendations or financial advice
- Broker/exchange connectivity, autonomous execution, or real-capital orders

## Acceptance criteria

- The two preview paths are available through API and CLI.
- Evidence is retained atomically under the configured storage root.
- Missing fixtures, live executor absence, and budget violations are explicit and fail closed.
- Tests cover positive and negative boundaries.
- Manual usage, traceability, OpenSpec, exit evidence, and hosted Quality are current before P12 is complete.

## Dependencies

P7-P11 and M9-M10 contracts.
