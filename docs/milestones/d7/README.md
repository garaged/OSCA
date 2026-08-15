# D7 — Visual Strategy Builder and Backtest Lab

- **Status:** Draft for implementation
- **Baseline:** D6 merge `9d7210011f0bc86b8e811ae92796d84ebc3c10ab`
- **Intent:** `intent.md`
- **Requirements:** `../../governance/requirements-catalog-d7.md`
- **Specification:** `specification.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Validation evidence:** `validation-evidence.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d7-strategy-builder-backtest-lab/`

## Outcome

D7 introduces a desktop research lab for defining versioned strategies through guided declarative rules and evaluating those strategies against governed historical data under explicit assumptions.

The milestone remains research-only. It does not create recommendation generation, automatic promotion, brokerage connectivity, paper-order submission, live-order routing, or real-capital execution.

## Initial slices

1. D7 requirements, specification, OpenSpec, traceability, manual acceptance, validation evidence, and exit review baseline.
2. Python strategy-definition service, DSL validation, persistence, migration, and desktop methods.
3. Python backtest service with deterministic vectorized baseline, provenance, assumptions, metrics, and evidence retention.
4. Strategy Builder and Backtest Lab UI with accessibility, responsive behavior, chart/table parity, and export coverage.
5. Sensitivity, walk-forward, benchmark comparison, D6 project pinning, and final exit reconciliation.

## Exit gate

D7 exits only after implementation, hosted validation, and complete clean-profile manual acceptance pass on:

- macOS ARM64;
- Linux x86-64.
