# u4-common-quantitative-analysis Specification

## Purpose

Provide deterministic descriptive and technical analysis over governed OHLCV datasets without creating advice or execution capability.

## Requirements

### Requirement: Governed single-dataset analysis

U4 SHALL calculate quantitative analysis only from an explicit dataset revision and governed payload selected through the U2 runtime.

#### Scenario: An analysis is requested
- **GIVEN** an explicit governed OHLCV payload and dataset revision
- **WHEN** the U4 runtime is called
- **THEN** it validates and loads the source through U2 before calculating analysis.

### Requirement: Point-in-time technical series

U4 SHALL provide returns, cumulative performance, drawdown, RSI, ROC, MACD, ATR, Bollinger bands, OBV, and trend/volatility regimes using only current and earlier observations.

#### Scenario: A technical series is produced
- **GIVEN** a chronologically ordered OHLCV series
- **WHEN** a point-in-time indicator is calculated
- **THEN** unavailable warm-up values remain null and no future observation influences an earlier value.

### Requirement: Explicit descriptive assumptions

U4 SHALL provide annualized return and volatility, downside volatility, Sharpe, Sortino, historical VaR/CVaR, distribution statistics, outlier counts, autocorrelation, and drawdown duration with explicit parameters and assumptions.

#### Scenario: A summary is inspected
- **GIVEN** a completed analysis
- **WHEN** summary evidence is returned
- **THEN** periods-per-year, risk-free rate, confidence level, formulas, small-sample findings, and descriptive-not-predictive VaR/CVaR semantics are visible.

### Requirement: Exact cross-dataset alignment

U4 SHALL calculate correlation, beta, and rolling correlation only over exact shared timestamps unless a future governed alignment policy supersedes this rule.

#### Scenario: Two datasets have different timestamp coverage
- **GIVEN** two governed datasets with partially overlapping timestamps
- **WHEN** comparison analysis is requested
- **THEN** only exact shared timestamps are used and no resampling, interpolation, or forward filling occurs.

### Requirement: Provenance and safety boundaries

U4 SHALL record source revisions, payload digests, parameters, assumptions, findings, input/output digests, and disabled network, credential, recommendation, broker, and real-capital boundaries.

#### Scenario: Analysis evidence is exported
- **GIVEN** a completed analysis
- **WHEN** the JSON or API result is retained
- **THEN** its provenance and assumptions remain inspectable and no execution capability is enabled.
