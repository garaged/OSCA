# P12 - Local Model-Assisted Preview

- **Status:** Implementation candidate, review ready
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Add opt-in, evidence-retaining local model previews with explicit budgets and fail-closed LLM boundaries.
- **Baseline:** Completed M0-M12 roadmap and P1-P11
- **Last reviewed:** 2026-07-31
- **Validation:** Quality run `30645896227` passed on PR #55

## Objective

Provide one deterministic local inference path and one fixture-backed LLM analysis path without making a paid model, network connection, or model provider a platform dependency.

## User-visible value

Users can experiment with model-assisted analysis, retain exact model/input/prompt/budget evidence, and see when a request is blocked, unavailable, over budget, or awaiting human review.

## Implementation scope

- Deterministic ordinary-least-squares trend preview over explicit numeric evidence.
- Fixture-backed LLM analysis preview with exact provider/model/prompt identity.
- Immutable budget, request, status, review, and evidence contracts.
- Input digests, model identity, prompt version, output, metrics, findings, cost, latency, and safety boundaries.
- Atomic local evidence retention under `model-preview/`.
- CLI commands through `python -m osca.model_preview`.
- Network/model calls disabled by default.

## Explicit behavior

- Local trend preview uses no network and has zero estimated cost.
- LLM fixture output is always `review_required` and labeled not financial advice.
- Missing fixture plus disabled network returns `policy_blocked`.
- Explicit live-model checks return `provider_unavailable` until a separately governed executor exists.
- Budget violations return `budget_exceeded` without output.

## Explicit non-scope

- Remote model invocation or credential resolution.
- Production model serving, automated retraining, or model promotion.
- Authoritative recommendations, autonomous actions, brokers, or real-capital orders.

## Validation evidence

- Ruff passed.
- Strict mypy passed across 193 source files.
- 324 tests passed, including all seven P12 tests.
- Contracts, migrations, document links, and architecture checks passed.
- OpenSpec doctor and strict validation passed.
- Secret scanning passed.

## Acceptance criteria

- REQ-0240-REQ-0246 map to implementation and tests.
- Model, input, prompt, budget, output, review state, and provenance remain inspectable.
- Network/model calls remain disabled unless a future governed milestone enables an executor.
- Automated tests cover success, budget, block, unavailable, retention, and CLI behavior.
- Documentation, OpenSpec, traceability, manual usage, and hosted Quality are current.

## Dependencies

P7-P11 retained evidence plus M9-M10 ML/LLM governance contracts.

## Risks and decisions

- P12 is optional and must not weaken the deterministic P6-P11 workflow.
- Fixture output is untrusted until reviewed.
- Cost, privacy, hallucination, and data-disclosure controls fail closed.
