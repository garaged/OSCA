# OSCA Backtest-to-Paper Evidence Report

## Validation context

- Milestone: P8 Backtest-to-Paper Happy Path
- Validation date: 2026-07-31
- Environment: macOS Apple Silicon, Python 3.13, `uv`
- Workflow: P6 local import -> P7 deterministic research -> P8 backtest-to-paper evidence
- Fixture: `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv`
- Imported row count: 10
- Evidence retained from the successful local manual-validation run

## Scope

- Project: `p8-backtest-paper-happy-path`
- Symbol: `AAPL`
- Timeframe: `1d`
- Strategy: `sma-trend-long-only`
- Evidence only: `True`
- Not financial advice: `True`

## Backtest

| Metric | Value |
|---|---:|
| Bars processed | 10 |
| Signal bars | 6 |
| Initial cash | 10000.00 |
| Final equity | 10370.37 |
| Strategy return | 0.037037 |
| Buy-and-hold return | 0.160000 |
| Max drawdown | -0.017544 |
| Evidence trades | 3 |

## Paper Evaluation

- Paper run: `aaad0f77-aebd-455b-832a-9df9feafb680`
- Mode: `local-evidence-only`
- Comparison: The built-in strategy underperformed buy-and-hold by `-0.122963` over the supplied local evidence window.

## Safety boundary confirmation

The validation did not enable live providers, broker connections, investment recommendations, autonomous execution, production ingestion, credential materialization, or real-capital orders.
