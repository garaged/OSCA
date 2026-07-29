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
- Compute deterministic return, volatility, drawdown, simple moving average, and data-quality summaries.
- Render report output in CLI JSON plus static Markdown or JSON file form.
- Document the first-run workflow.

## Explicit non-scope

- ML, LLM, recommendations, production ingestion, scheduler execution.

## Acceptance criteria

- The milestone objective is demonstrable from the shared application API and `osca demo-research-report` CLI command.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P6 local OHLCV import.

## Risks and decisions

The report must communicate evidence and limitations without implying financial advice.


## Workflow contract

P7 consumes the canonical OHLCV Parquet payload written by P6 and does not invoke provider APIs or materialize credentials.

The report workflow must retain the requested demo project name, symbol, timeframe, metric summary, quality summary, observations, and disabled deferred-boundary flags.

## Metric contract

P7 computes deterministic evidence metrics from closing prices:

- total return across the payload window
- mean period return
- sample volatility over period returns
- max drawdown
- simple moving averages for windows 3 and 5 when enough bars exist

## Reporting contract

P7 writes CLI JSON for automation and optionally writes a static Markdown or JSON report file for first-run user inspection.

Reports must state that the output is evidence-only, is not financial advice, and does not include recommendations.
