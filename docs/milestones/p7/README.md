# P7 - First Demo Research Workflow

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Minimum usable local/demo tool
- **Authoritative outcome:** Connect imported or bundled data to a narrow analyst workflow that produces a deterministic research report.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p7-demo-research-workflow.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p7-demo-research-workflow/spec.md)

## Objective

Connect imported or bundled data to a narrow analyst workflow that produces a deterministic research report.

## User-visible value

A user can run one command or simple local flow and get useful market observations from OSCA.

## Implementation scope

- Add a demo project/watchlist.
- Compute basic deterministic indicators, returns, volatility, drawdown, and data-quality summaries.
- Render report output in CLI and static file form.
- Document the first-run workflow.

## Explicit non-scope

- ML, LLM, recommendations, production ingestion, scheduler execution.

## Acceptance criteria

- REQ-0205-REQ-0211 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P6 local OHLCV import.

## Risks and decisions

The report must communicate evidence and limitations without implying financial advice.
