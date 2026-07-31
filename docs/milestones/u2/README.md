# U2 - Analytical Data Runtime and Chart-Series API

- **Status:** Planned
- **Baseline:** U1 merge `4717a8d24582e564c23497127e0c211e849e25c8`
- **Phase:** Analysis, visualization, and ML experiments
- **Roadmap:** [U2-U7 roadmap](../analysis-visualization-ml-roadmap.md)

## Objective

Create the shared point-in-time analytical runtime required by visualization, common analysis, backtesting reuse, and ML feature generation.

## User-visible value

An operator can select a governed OHLCV dataset and obtain bounded chart-ready data plus initial derived series with complete provenance and honest warnings.

## Implementation scope

- Dataset/revision-based OHLCV query contract.
- Bounded date/range and row-count requests.
- Chart rows for timestamp, OHLC, volume, interval, completeness, source, and revision.
- Deterministic downsampling for large series while preserving extrema and range identity.
- Shared derived-series definitions for simple return, log return, SMA, EMA, rolling volatility, and rolling volume.
- Warm-up/null semantics and point-in-time safety checks.
- Parameter, input digest, output digest, timing, warnings, and findings evidence.
- JSON API/CLI suitable for the existing analyst workspace.
- Fixture and property-style formula validation.

## Architecture decision required at entry

Select the smallest numerical/dataframe dependency set that:

- supports Python 3.13 on Linux x86_64 and macOS arm64;
- has acceptable licensing and packaging;
- avoids binary-float ambiguity in persisted canonical market data;
- provides deterministic tested analytical output;
- does not make a notebook runtime mandatory.

## Explicit non-scope

- Interactive browser charts, owned by U3.
- Full indicator library, owned by U4.
- ML training, owned by U5.
- Remote data discovery or provider calls.
- Recommendations, broker connectivity, autonomous execution, or real orders.

## Acceptance criteria

- The committed AAPL fixture can be imported and queried into chart-ready OHLCV JSON.
- Date/range bounds and maximum-row budgets fail closed.
- Downsampled output preserves first/last points and material highs/lows under documented rules.
- Initial derived series match independent expected fixtures and never use future observations.
- Every response records dataset/revision identity and transformation provenance.
- Hosted Quality and clean-machine manual validation pass.
