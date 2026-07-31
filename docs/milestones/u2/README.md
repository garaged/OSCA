# U2 - Analytical Data Runtime and Chart-Series API

- **Status:** Implementation candidate
- **Baseline:** U2-U7 roadmap merge `70063a706aea6f1cb785a9de4a8f5eebd05509d5`
- **Phase:** Analysis, visualization, and ML experiments
- **Roadmap:** [U2-U7 roadmap](../analysis-visualization-ml-roadmap.md)

## Objective

Create the shared point-in-time analytical runtime required by visualization, common analysis, backtesting reuse, and ML feature generation.

## User-visible value

An operator can select an explicit governed OHLCV payload/revision and obtain bounded chart-ready data plus initial derived series with provenance and safety boundaries.

## Implemented scope

- Immutable dataset-revision and payload query contracts.
- Bounded date/range and row-count requests.
- Chart rows for timestamp, OHLC, volume, completeness, symbol, timeframe, and revision.
- Deterministic evenly-spaced downsampling preserving first and last observations.
- Shared derived-series definitions for simple return, log return, SMA, EMA, rolling volatility, and rolling volume.
- Explicit warm-up/null semantics and point-in-time-safe calculations.
- Parameters, input digest, output digest, payload digest, and downsampling evidence.
- JSON CLI through `python -m osca.analytical_data query`.
- Automated formula, filtering, deterministic-downsampling, validation, and safety-boundary coverage.

## Dependency decision

U2 adds no new numerical or dataframe dependency. The existing PyArrow dependency reads governed Parquet payloads; standard-library math implements the initial transparent transformations. This minimizes licensing, wheel, packaging, and reproducibility risk. U3 and U4 must separately review any charting or expanded numerical dependencies they introduce.

## Explicit non-scope

- Interactive browser charts, owned by U3.
- Extrema-aware visual aggregation, which may be added in U3 when chart rendering requirements are concrete.
- Full indicator library, owned by U4.
- ML training, owned by U5.
- Remote data discovery or provider calls.
- Recommendations, broker connectivity, autonomous execution, or real orders.

## Acceptance criteria

- A governed Parquet OHLCV payload can be queried into chart-ready JSON.
- Invalid paths, ranges, schemas, OHLC values, timestamps, and row budgets fail closed.
- Downsampled output is deterministic and preserves first/last points.
- Initial derived series match expected formulas and never use future observations.
- Every response records revision identity, payload digest, transformation digests, and disabled external/capital boundaries.
- Hosted Quality and clean-machine manual validation pass.

## Manual command

```bash
uv run python -m osca.analytical_data query \
  <payload.parquet> <dataset-revision-uuid> AAPL 1d \
  --derived simple_return \
  --derived sma:3 \
  --derived ema:3 \
  --max-rows 2000
```
