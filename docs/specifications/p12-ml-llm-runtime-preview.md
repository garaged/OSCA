# P12 ML/LLM Runtime Preview Specification

## Purpose

Turn governed ML and LLM lifecycle contracts into opt-in local runtime previews with budgets, provenance, and fail-closed controls.

## Phase

Useful analyst workflow

## User-visible value

Users can experiment with model-assisted analysis while retaining evidence and cost/privacy boundaries.

## Requirements

- REQ-0240-REQ-0246: OSCA must implement the P12 scope described by this specification before P12 is marked complete.
- REQ-0240-REQ-0246: P12 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0240-REQ-0246: P12 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Implement one small ML training/inference path over imported data.
- Implement optional LLM analysis generation through existing gateway contracts.
- Record budgets, inputs, prompts, model identity, outputs, and review status.
- Disable network/model calls by default.

## Explicit non-scope

- Autonomous recommendations, production model serving, real orders.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P7-P11 and M9-M10 contracts.

## Risks and decisions

Cost, privacy, and hallucination boundaries require explicit validation.
