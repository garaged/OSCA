# P8 - Backtest-to-Paper Happy Path

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Pending hosted Quality

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p8-backtest-paper-happy-path.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p8-backtest-paper-happy-path/spec.md)
- [User testing quickstart](user-testing-quickstart.md)

## Objective

Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records.

## User-visible value

Users can compare a strategy hypothesis against historical data and retain paper-evaluation evidence.

## Implementation scope

- Implement one built-in transparent strategy.
- Execute deterministic backtests from imported data.
- Publish F2/F3 evidence bundles and comparison summaries.
- Expose shared application contracts plus CLI commands for run, inspect, and export.

## Explicit non-scope

- Live paper broker integration, real orders, autonomous execution.

## Acceptance criteria

- REQ-0212-REQ-0218 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P7 demo workflow, M6-M8 validation foundations.

## Risks and decisions

Strategy results must be framed as validation evidence, not performance promises.


## Implementation candidate

P8 adds the `osca.backtest_paper` package and `osca backtest-paper-run` CLI command.

The happy path consumes a canonical P6 OHLCV Parquet payload and produces:

- A built-in transparent `sma-trend-long-only` strategy hypothesis.
- Deterministic backtest evidence over the supplied local bars.
- Strategy return, buy-and-hold comparison, max drawdown, exposure, and evidence trade count.
- A local paper-evaluation record linked to the backtest request.
- CLI JSON plus optional static Markdown or JSON evidence report output.
- Fail-closed deferred boundaries for live brokers, autonomous execution, recommendations, and real orders.

P8 remains evidence-only. It does not implement live paper broker integration, autonomous strategy execution, recommendations, or real-capital orders.
