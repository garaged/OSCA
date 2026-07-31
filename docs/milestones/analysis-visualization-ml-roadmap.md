# Analysis, Visualization, and ML Experiment Roadmap

- **Status:** Proposed
- **Baseline:** U1 merge `4717a8d24582e564c23497127e0c211e849e25c8`
- **Phase:** Usable local research product
- **Sequence:** U2 through U7

## Product objective

Turn OSCA's governed local data and evidence foundations into an approachable visual research environment where an operator can inspect OHLCV and other available datasets, run common quantitative analysis, compare results, and execute reproducible local ML prediction experiments.

The phase remains research-only. Outputs are observations, diagnostics, experiments, and paper evidence—not investment advice or authorization to place orders.

## Foundation assessment

OSCA already has:

- governed OHLCV import, temporal correctness, Parquet payloads, and dataset revisions;
- M4 analysis graph, analytical output, and visualization contracts;
- deterministic research, backtesting, paper evidence, and a read-only workspace;
- M9 feature, label, experiment, model artifact, evaluation, promotion, and monitoring contracts;
- P12 deterministic model previews;
- U1 first-run diagnostics.

Two runtime foundations are still required:

1. A reusable point-in-time analytical dataset and indicator runtime that can feed charts, reports, backtests, and ML without duplicating transformations.
2. A local trainer/experiment executor that materializes M9 evidence while preventing leakage, unsafe splitting, and automatic promotion.

U2 delivers the first foundation together with immediately visible chart-ready data. U5 delivers the second only after deterministic analysis and visualization are useful.

## Milestone sequence

| Milestone | Outcome | Main user value |
|---|---|---|
| U2 | Analytical data runtime and chart-data API | Load a governed dataset once and obtain bounded OHLCV, derived series, provenance, warnings, and downsampled chart payloads. |
| U3 | Interactive market-data visualization | Candlestick/OHLC, volume, line/area, range selection, crosshair, zoom, timeframe selection, overlays, and export in the local workspace. |
| U4 | Common quantitative analysis library | Trend, momentum, volatility, volume, return/risk, drawdown, distribution, correlation, regime, and data-quality analysis with parameter and lineage evidence. |
| U5 | Governed local ML experiment runner | Define features/labels, run time-aware baselines, retain artifacts/metrics, and compare experiments without network or automatic promotion. |
| U6 | Prediction lab and visual diagnostics | Visualize predictions, confidence/calibration, residuals, feature importance, walk-forward performance, and baseline comparisons. |
| U7 | Model-to-research validation | Link an approved experiment to event-driven/backtest and paper-challenger evidence without live serving, recommendations, or orders. |

## U2 — Analytical data runtime

Required before richer visualization or ML.

- Read governed Parquet OHLCV through dataset identity/revision, not arbitrary silent file discovery.
- Normalize chart rows with timestamp, OHLC, volume, source identity, interval, and completeness state.
- Provide bounded date/range queries and deterministic largest-triangle or bucket-based downsampling where needed.
- Add derived-series contracts with warm-up/null semantics, parameter identity, input digest, and output digest.
- Start with returns, log returns, SMA, EMA, rolling volatility, and volume averages.
- Preserve point-in-time safety and prohibit future-data access.
- Expose JSON APIs usable by the workspace and later ML feature generation.

## U3 — Visualization

- Extend the loopback-only workspace rather than introduce a separate public service.
- Use a browser-native chart library only after license, offline bundling, CSP, dependency, and export review.
- Required views: candlestick/OHLC, close/adjusted line when available, volume, indicator panels, drawdown, and return distribution.
- Required interaction: zoom, pan, crosshair, tooltip, date range, timeframe, series visibility, and reset.
- Clearly show gaps, incomplete bars, stale evidence, source/provider, dataset revision, and indicator warm-up regions.
- Export the visible chart as PNG/SVG where supported and export chart data as CSV/JSON with provenance.

## U4 — Common analysis

Initial built-in analyses:

- **Price/returns:** simple and log returns, cumulative return, rolling return, highs/lows, gaps.
- **Trend:** SMA/EMA, moving-average distance/crosses, linear trend slope and fit quality.
- **Momentum:** RSI, rate of change, MACD.
- **Volatility/range:** rolling standard deviation, ATR, Bollinger bands, downside volatility.
- **Volume:** rolling volume, volume change, on-balance volume when volume is meaningful.
- **Risk:** drawdown, maximum drawdown, recovery duration, historical VaR/CVaR as descriptive estimates, Sharpe/Sortino with explicit assumptions.
- **Distribution:** mean, median, dispersion, skewness, kurtosis, quantiles, outliers, autocorrelation.
- **Relationships:** aligned correlation/beta and rolling correlation for multiple governed datasets.
- **Regime/data quality:** volatility/trend regimes, missing bars, duplicates, stale/incomplete observations.

Every result records parameters, assumptions, warm-up requirements, source revisions, timestamps, and findings. No metric is presented as a recommendation.

## U5 — ML experiment runner

- Add an explicit local execution adapter behind existing M9 contracts.
- Begin with transparent baselines: persistence/naive forecast, moving-average forecast, linear/ridge regression, and logistic classification.
- Add tree-based models only after dependency and reproducibility review.
- Support regression targets such as future return and volatility, and classification targets such as direction or threshold events.
- Enforce chronological train/validation/test splits, purge/embargo where overlapping labels require it, fit transformations on training data only, and walk-forward evaluation.
- Compare against naive baselines and reject experiments with leakage findings or insufficient samples.
- Retain feature/label definitions, dataset/code revisions, seeds, parameters, metrics, predictions, artifact digests, timings, and environment identity.
- No remote trainer, GPU requirement, hyperparameter cloud service, automatic retraining promotion, or production serving.

## U6 — Prediction lab

- Dataset, feature-set, label, split, and model selectors.
- Experiment comparison table with baseline-relative metrics.
- Prediction-vs-actual overlays and directional correctness markers.
- Residual/error distributions, calibration/reliability plots, confusion matrix, ROC/PR where appropriate.
- Feature coefficient/importance evidence with warnings against causal interpretation.
- Walk-forward fold and regime breakdowns.
- Explicit status labels: exploratory, invalid, review-required, eligible-for-F2-validation.

## U7 — Validation integration

- Only models passing M9 promotion gates may enter F2 event-driven validation.
- Compare model signals against deterministic and naive baselines with transaction-cost assumptions.
- Support paper challenger evidence only through an explicit human decision.
- Retain prediction, signal, trade, reconciliation, drift, and outcome links.
- No live model serving, broker connectivity, autonomous scheduling into capital, or real orders.

## Cross-cutting acceptance

- Works from local/imported OHLCV without paid services.
- Supports stocks and crypto under their existing temporal/calendar semantics.
- Deterministic fixture and synthetic-data tests cover all formulas and leakage boundaries.
- Large-series behavior is bounded and measured.
- Accessibility, responsive layout, empty/error states, and manual workflows are documented.
- Every milestone updates OpenSpec, requirements/traceability, manual testing, exit review, and hosted Quality evidence.
- ADR-0044 remains authoritative throughout.

## Dependency decisions deferred to implementation

U2 must decide the smallest suitable numerical/analytical dependency set. U3 must decide the chart library after licensing and offline-use review. U5 must decide whether scikit-learn is accepted as the initial local trainer dependency. These decisions should be made in their owning milestone and recorded before code depends on them.
