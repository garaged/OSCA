# D7 Specification — Visual Strategy Builder and Backtest Lab

## Summary

D7 is a desktop research and reproducibility milestone. It lets users define versioned strategy rules through a guided declarative DSL, evaluate them with explicit assumptions, compare benchmarks, inspect results, and retain governed evidence.

Python remains authoritative for strategy definitions, DSL validation, data integrity checks, backtest execution, metrics, persistence, migration, provenance, and export. React renders typed state and captures declarative intent. Rust remains the existing transport/session broker and ownership boundary.

## Requirements

D7 implements `REQ-0357` through `REQ-0374` in `docs/governance/requirements-catalog-d7.md`.

## Domain Model

### Strategy Definition

A strategy definition includes:

- stable strategy ID;
- normalized unique name;
- objective;
- asset universe reference;
- timeframe;
- tags;
- status;
- creation/update metadata;
- current version pointer.

### Strategy Version

A strategy version is immutable after creation and includes:

- version ID and sequence;
- DSL document;
- template origin, if any;
- validation result digest;
- human-readable summary;
- created-at metadata;
- superseded-by pointer, if any.

### Rule DSL

The DSL is typed and declarative. It represents:

- entry rules;
- exit rules;
- filters;
- sizing rules;
- risk controls;
- cost and slippage assumptions;
- benchmark selection;
- run constraints.

The DSL cannot contain arbitrary code, SQL, shell commands, notebook cells, provider calls, filesystem paths, broker instructions, or executable snippets.

### Backtest Run

A backtest run includes:

- run ID;
- strategy version ID;
- governed dataset revision references;
- engine and fidelity level;
- assumptions;
- run window;
- benchmark references;
- seed or deterministic-order metadata where applicable;
- warnings and degraded states;
- result evidence references.

### Result Evidence

Result evidence includes:

- metrics;
- equity curve;
- drawdown series;
- trade list;
- exposure summary;
- benchmark comparison;
- sensitivity or walk-forward outputs where applicable;
- schema version, producer version, digest, and export metadata.

## Functional Behavior

### Strategy Builder

Users can create, validate, version, clone, archive, and inspect strategies. Editing a strategy creates a new immutable version rather than mutating historical versions.

### Validation

Validation blocks:

- unknown rule types;
- missing or invalid parameters;
- incompatible indicator/timeframe/asset combinations;
- invalid sizing or risk rules;
- future-data references;
- look-ahead expressions;
- unsorted or duplicate timestamps;
- missing required OHLCV columns;
- invalid train/test partitions.

Validation failures must be visible and must prevent backtest execution.

### Backtest Execution

Backtests run only in Python against governed datasets. D7 supports:

- a deterministic vectorized research fidelity level;
- an event-driven simulation fidelity level when its assumptions are explicit;
- conservative cost and slippage defaults;
- bounded run budgets;
- cancellation with retained failed/cancelled status;
- restart-safe persisted state.

### Results and Inspection

The UI presents result charts, tables, assumptions, warnings, and synchronized chart/table observations. Users must be able to inspect values by keyboard and pointer, export full-resolution evidence, and distinguish display downsampling from authoritative result data.

### Sensitivity and Walk-Forward

Sensitivity and walk-forward views must declare their parameter ranges, budgets, train/test windows, and overfitting warnings. Hidden reuse of future observations is prohibited.

### D6 Integration

D7 can pin strategy definitions and result evidence into D6 projects through typed references. It must not duplicate large provider datasets in project exports.

## Boundaries

D7 does not add:

- recommendation generation;
- automatic strategy promotion;
- brokerage connectivity;
- paper-order submission;
- live-order routing;
- real-capital execution;
- arbitrary user code execution;
- notebooks;
- external provider credential collection.

## Accessibility and Responsiveness

D7 must support keyboard operation, visible focus, screen-reader labels, reduced-motion and forced-colors behavior, and responsive 320/680 CSS-pixel layouts for the strategy builder, result charts, tables, controls, and empty/loading/error states.

## Exit Criteria

- `REQ-0357` through `REQ-0374` are traceably implemented or explicitly dispositioned.
- Strict OpenSpec, architecture, secret, Python, frontend, Rust, migration, and packaging gates pass.
- Clean-profile manual acceptance passes on macOS ARM64 and Linux x86-64.
- Exit evidence records assumptions, limitations, hosted validation, manual acceptance, and the final decision.
