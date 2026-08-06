# Test fixture provenance

Files under this directory are deterministic test inputs created for OSCA validation unless a file-specific notice states otherwise.

## Local OHLCV fixture

`local_ohlcv/aapl_backtest_daily.csv` is synthetic data created for deterministic import, research, backtest, and desktop-onboarding tests.

- `AAPL` is a scenario label only.
- The rows are not actual Apple Inc. market observations.
- The values are not sourced from a market-data provider.
- The fixture must not be presented as current, historical, or investment-grade market data.
- The fixture is distributed under the repository's Apache License 2.0 as original OSCA test material.

Do not add real provider responses or market datasets unless their provenance and redistribution rights are documented and explicitly permit public repository distribution. Do not add credentials, user profiles, generated research evidence, or restricted provider content.
