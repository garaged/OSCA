# P8 - Backtest-to-Paper Happy Path

- **Status:** Complete
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records.
- **Baseline:** Completed M0-M12 roadmap and P1-P7
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality and macOS Apple Silicon manual validation passed

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p8-backtest-paper-happy-path.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p8-backtest-paper-happy-path/spec.md)
- [User testing quickstart](user-testing-quickstart.md)
- [Exit review](exit-review.md)
- [Retained manual evidence](../../../evidence/p8/manual-backtest-paper-report.md)

## Objective

Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records.

## User-visible value

Users can compare a strategy hypothesis against historical data and retain paper-evaluation evidence.

## Implemented scope

- One built-in transparent `sma-trend-long-only` strategy.
- Deterministic backtests from imported P6 OHLCV data.
- Strategy return, buy-and-hold comparison, max drawdown, exposure, signal-bar, and evidence-trade metrics.
- A linked local paper-evaluation record.
- CLI JSON plus optional Markdown or JSON static evidence reports.
- Fail-closed validation for missing/invalid payloads and fewer than five bars.

## Explicit non-scope

- Live paper broker integration.
- Real orders or autonomous execution.
- Investment recommendations or financial advice.
- Live provider routing, credential materialization, or production ingestion.

## Completion evidence

- PR #44 implemented P8 and passed hosted Quality.
- PRs #45-#48 corrected Python 3.13/macOS ARM64 compatibility and strict typing findings; their hosted Quality runs passed.
- PRs #49-#51 corrected the real manual workflow, fixture path, CLI argument shape, shell-safe payload handoff, and five-bar minimum documentation; their hosted Quality runs passed.
- The final macOS Apple Silicon workflow imported `aapl_backtest_daily.csv` with `row_count: 10`, processed 10 AAPL daily bars, generated 3 simulated evidence trades, and remained in `local-evidence-only` mode.

## Dependencies

P7 demo workflow and M6-M8 validation foundations.

## Residual boundaries

P8 is evidence-only. It does not implement live paper broker integration, autonomous strategy execution, recommendations, live-provider ingestion, credential materialization, production routing, or real-capital orders.
