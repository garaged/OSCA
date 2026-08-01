# U4 - Common Quantitative Analysis

- **Status:** Implementation candidate
- **Depends on:** U2-U3
- **Baseline:** U3 merge `58b9ddf0cc377861c3ce84a2c1f7a759486a3f24`

## Objective

Provide a validated built-in library of common descriptive and technical analysis over explicit governed datasets.

## Implemented scope

### Point-in-time series

- Close-to-close simple returns and cumulative performance.
- Drawdown and recovery-duration evidence.
- RSI and rate of change.
- MACD, signal, and histogram.
- ATR and Bollinger bands.
- On-balance volume.
- Fast/slow-EMA trend regimes.
- Rolling-return volatility regimes.

All series retain warm-up nulls where applicable and use only current and earlier observations.

### Descriptive summary

- Total and annualized return.
- Annualized and downside volatility.
- Sharpe and Sortino ratios.
- Maximum drawdown and duration.
- Historical empirical VaR and CVaR.
- Mean, median, standard deviation, quantiles, skewness, and excess kurtosis.
- Minimum/maximum returns, lag-one autocorrelation, and three-sigma outlier count.

Parameters and assumptions explicitly identify periods per year, risk-free rate, confidence level, formula semantics, and the descriptive-not-predictive nature of historical VaR/CVaR.

### Multi-dataset comparison

- Exact shared-timestamp alignment.
- Full-period correlation and beta.
- Rolling correlation.
- No resampling, interpolation, timezone conversion, or forward filling.

### Operator surfaces

- `python -m osca.quantitative_analysis` for JSON evidence.
- `/api/quantitative-analysis` in the loopback-only analyst workspace.
- Result contracts suitable for U3 visualization and later U5 feature review.

## Dependency decision

U4 adds no new numerical dependency. Existing PyArrow and standard-library math remain sufficient for transparent deterministic formulas. A specialized numerical dependency can be reconsidered in U5 if governed model training requires it.

## Evidence and safety

Every result records dataset revision, payload digest, parameters, assumptions, findings, input/output digests, and point-in-time status. Network access, credentials, recommendations, broker execution, and real-capital behavior remain disabled.

## Non-scope

- Investment advice or target prices.
- Automatic strategy or indicator selection.
- ML training or prediction.
- Silent dataset alignment or synthetic missing values.
- Brokers, autonomous execution, or real orders.

## Acceptance

- Independent deterministic fixtures cover formulas, warm-up behavior, drawdown, risk summaries, exact timestamp alignment, and API evidence.
- The runtime fails closed for invalid window ordering and invalid governed payloads.
- Hosted Quality and manual clean-machine review pass before merge.
