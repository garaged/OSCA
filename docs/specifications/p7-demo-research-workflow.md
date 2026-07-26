# P7 First Demo Research Workflow Specification

## Purpose

Connect imported or bundled data to a narrow analyst workflow that produces a deterministic research report.

## Phase

Minimum usable local/demo tool

## User-visible value

A user can run one command or simple local flow and get useful market observations from OSCA.

## Requirements

- REQ-0205-REQ-0211: OSCA must implement the P7 scope described by this specification before P7 is marked complete.
- REQ-0205-REQ-0211: P7 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0205-REQ-0211: P7 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Add a demo project/watchlist.
- Compute basic deterministic indicators, returns, volatility, drawdown, and data-quality summaries.
- Render report output in CLI and static file form.
- Document the first-run workflow.

## Explicit non-scope

- ML, LLM, recommendations, production ingestion, scheduler execution.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P6 local OHLCV import.

## Risks and decisions

The report must communicate evidence and limitations without implying financial advice.
