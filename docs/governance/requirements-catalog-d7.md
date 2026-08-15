# D7 Requirements Catalog — Visual Strategy Builder and Backtest Lab

Status: Draft for implementation
Baseline: D6 merge `9d7210011f0bc86b8e811ae92796d84ebc3c10ab`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0357 | D7 shall provide profile-scoped, versioned research strategy definitions with stable identity, normalized unique name, objective, asset universe reference, timeframe, creation metadata, and immutable version records. | Strategy service, persistence, migration, and desktop API tests |
| REQ-0358 | Strategy definitions shall be expressed through a typed declarative DSL and guided templates; React shall not execute arbitrary code, notebooks, shell commands, SQL, provider calls, or strategy logic. | DSL parser/validator, frontend source-boundary, and Rust/API tests |
| REQ-0359 | Entry, exit, filter, sizing, risk-control, cost, and benchmark rules shall be validated for type compatibility, required parameters, asset/timeframe compatibility, and unsupported combinations before any backtest can run. | Rule validation, negative, and property tests |
| REQ-0360 | D7 shall detect and block obvious look-ahead, future-data, unsorted-time, duplicate-observation, missing-column, and non-monotonic-series inputs with user-visible explanations. | Bias/integrity tests and manual acceptance |
| REQ-0361 | Backtests shall run through authoritative Python services using governed dataset revisions and shall record every dataset, strategy version, engine, assumption, and parameter used to produce a result. | Backtest service, provenance, and restart tests |
| REQ-0362 | D7 shall support explicit fidelity levels, including vectorized research evaluation and event-driven simulation, and shall disclose the limits of each level before and after execution. | Fidelity contract tests and UI disclosure checks |
| REQ-0363 | D7 shall model costs, slippage, fills, cash, position sizing, and rejected/invalid orders only as research assumptions; assumptions shall default conservatively and remain visible in result evidence. | Cost/fill/accounting tests and manual acceptance |
| REQ-0364 | D7 shall compute deterministic backtest metrics, equity curves, drawdowns, trade lists, exposure summaries, and benchmark comparisons without modifying source datasets or strategy versions. | Golden metrics, no-mutation, and parity tests |
| REQ-0365 | D7 shall provide sensitivity and parameter-sweep views with bounded budgets, deterministic ordering, progress/cancellation behavior, and clear overfitting warnings. | Sweep budget, cancellation, and UI tests |
| REQ-0366 | D7 shall provide walk-forward or out-of-sample evaluation views with explicit train/test ranges and shall prevent hidden reuse of future observations in earlier windows. | Walk-forward partition and bias tests |
| REQ-0367 | Strategy and backtest results shall be retained as governed evidence with schema version, producer version, digest, warnings, assumptions, and degraded-state disclosure. | Evidence persistence/export tests |
| REQ-0368 | D7 shall allow saving strategy-lab views and pinning accepted strategy/backtest evidence into D6 projects without duplicating large provider datasets. | Workspace/project integration tests |
| REQ-0369 | D7 shall provide accessible keyboard, pointer, screen-reader, reduced-motion, forced-colors, and responsive 320/680 CSS-pixel operation for the strategy builder, result charts, tables, and comparison controls. | Frontend accessibility/responsive tests and supported-platform manual acceptance |
| REQ-0370 | D7 result charts and tables shall expose synchronized values, keyboard-selectable observations, x/y labels, assumptions, and full-resolution export/parity evidence. | Chart/table parity and export tests |
| REQ-0371 | D7 shall remain usable with local/sample/cached governed data without paid providers, network access, external accounts, or provider credentials. | Offline/source-boundary tests and clean-profile manual acceptance |
| REQ-0372 | D7 shall visibly preserve OSCA's research-only/no-recommendation/no-execution boundary and shall not create brokerage, paper-order, live-order, auto-promotion, or real-capital execution paths. | Source, UI, Rust boundary, and manual safety checks |
| REQ-0373 | Strategy storage and backtest result storage shall be profile-scoped, versioned, migratable, restart-safe, idempotent under interruption, and protected by the desktop ownership/locking boundary for mutations. | Migration, interruption, profile-isolation, and lock tests |
| REQ-0374 | D7 exit shall retain requirements, OpenSpec, traceability, migration/recovery evidence, automated validation, supported-platform manual acceptance, limitations, and accepted exit review evidence. | Exit review |
