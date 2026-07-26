# P12 - ML/LLM Runtime Preview

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Turn governed ML and LLM lifecycle contracts into opt-in local runtime previews with budgets, provenance, and fail-closed controls.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p12-ml-llm-runtime-preview.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p12-ml-llm-runtime-preview/spec.md)

## Objective

Turn governed ML and LLM lifecycle contracts into opt-in local runtime previews with budgets, provenance, and fail-closed controls.

## User-visible value

Users can experiment with model-assisted analysis while retaining evidence and cost/privacy boundaries.

## Implementation scope

- Implement one small ML training/inference path over imported data.
- Implement optional LLM analysis generation through existing gateway contracts.
- Record budgets, inputs, prompts, model identity, outputs, and review status.
- Disable network/model calls by default.

## Explicit non-scope

- Autonomous recommendations, production model serving, real orders.

## Acceptance criteria

- REQ-0240-REQ-0246 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P7-P11 and M9-M10 contracts.

## Risks and decisions

Cost, privacy, and hallucination boundaries require explicit validation.
