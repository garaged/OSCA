# P8 Backtest-to-Paper Happy Path Specification

## Purpose

Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records.

## Phase

Useful analyst workflow

## User-visible value

Users can compare a strategy hypothesis against historical data and retain paper-evaluation evidence.

## Requirements

- REQ-0212-REQ-0218: OSCA must implement the P8 scope described by this specification before P8 is marked complete.
- REQ-0212-REQ-0218: P8 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0212-REQ-0218: P8 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Implement one built-in transparent strategy.
- Execute deterministic backtests from imported data.
- Publish F2/F3 evidence bundles and comparison summaries.
- Expose CLI/API commands for run, inspect, and export.

## Explicit non-scope

- Live paper broker integration, real orders, autonomous execution.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P7 demo workflow, M6-M8 validation foundations.

## Risks and decisions

Strategy results must be framed as validation evidence, not performance promises.
