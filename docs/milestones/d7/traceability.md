# D7 Traceability

Status: implementation complete; hosted validation and manual acceptance pending

| Requirement | Planned implementation | Planned verification | Status |
|---|---|---|---|
| REQ-0357 | profile-scoped strategy definitions and immutable versions | strategy service, persistence, migration, restart tests | Implemented |
| REQ-0358 | typed declarative DSL and guided templates | parser/validator, frontend source-boundary, Rust/API tests | Implemented |
| REQ-0359 | rule compatibility and unsupported-combination validation | rule validation, negative, and property tests | Implemented |
| REQ-0360 | look-ahead and dataset-integrity blocking | bias/integrity tests and manual acceptance | Implemented |
| REQ-0361 | Python authoritative backtest service with provenance | service, provenance, and restart tests | Implemented |
| REQ-0362 | explicit fidelity levels and disclosures | contract tests and UI disclosure checks | Implemented |
| REQ-0363 | conservative research assumptions for costs/fills/accounting | cost/fill/accounting tests and manual acceptance | Implemented |
| REQ-0364 | deterministic metrics, curves, trades, exposure, benchmarks | golden metrics, no-mutation, and parity tests | Implemented |
| REQ-0365 | bounded sensitivity and parameter-sweep views | sweep budget, cancellation, and UI tests | Implemented |
| REQ-0366 | walk-forward/out-of-sample partitions | partition and bias tests | Implemented |
| REQ-0367 | governed result evidence retention | persistence/export tests | Implemented |
| REQ-0368 | D6 project pinning and view integration | workspace/project integration tests | Implemented |
| REQ-0369 | accessible responsive Strategy Lab UI | accessibility/responsive tests and manual acceptance | Implemented |
| REQ-0370 | chart/table synchronized inspection and export parity | chart/table parity and export tests | Implemented |
| REQ-0371 | offline local/sample/cached operation | offline/source-boundary tests and manual acceptance | Implemented |
| REQ-0372 | research-only/no-execution boundary | source, UI, Rust boundary, and manual safety checks | Implemented |
| REQ-0373 | profile-scoped versioned storage and ownership locks | migration, interruption, isolation, and lock tests | Implemented |
| REQ-0374 | retained D7 validation and exit evidence | validation evidence, traceability, manual acceptance, and exit review | Partial: implementation evidence retained; hosted/manual acceptance pending |

## Reused Authoritative Capabilities

D7 builds on D5 governed analysis/charting data and D6 project evidence organization. It references governed datasets and D6 project pins instead of broadening frontend authority or duplicating provider data.

## Planned D7 Methods

The planned typed method family is:

- `strategy.create`;
- `strategy.list`;
- `strategy.get`;
- `strategy.update`;
- `strategy.version.create`;
- `strategy.validate`;
- `strategy.archive`;
- `strategy.clone`;
- `backtest.prepare`;
- `backtest.run`;
- `backtest.cancel`;
- `backtest.get`;
- `backtest.list`;
- `backtest.export.prepare`;
- `backtest.sensitivity.run`;
- `backtest.walkforward.run`.

## Permanent D7 Boundary

D7 is a research and simulation milestone. It does not enable recommendations, strategy promotion, brokerage connectivity, paper orders, live orders, or real-capital execution.

## Closure

The blocking evidence is implementation, hosted validation, and the complete clean-profile manual procedure on macOS ARM64 and Linux x86-64.
