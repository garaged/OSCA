# D8 Exit Review — Virtual-Portfolio Accounting Foundation

## Decision

**PASS — accepted for merge.**

D8 met its intended outcome after exact-head hosted CI and full supported-platform manual acceptance. The milestone establishes a local-first, research-only virtual-portfolio accounting authority without introducing broker execution, recommendations, or real-capital operations.

## Exit criteria

- Independent profile-scoped virtual portfolios: PASS
- Decimal-safe authoritative accounting values: PASS
- Append-only economic events and balanced double-entry journals: PASS
- Deterministic cash/position/lot/book-cost/P&L/fee/income replay: PASS
- Explicit multi-lot disposal allocation with ambiguous requests failing closed: PASS
- Idempotent corporate actions and explicit corrections/reversals: PASS
- Multi-currency cash/FX and valuation provenance: PASS
- Explicit degraded state for incomplete price/FX evidence: PASS
- Clone/reset lineage without destructive source mutation: PASS
- Digest-protected portable export and atomic restore: PASS
- Immutable analytical snapshots, performance, and drawdown: PASS
- Per-asset attribution with provenance: PASS
- Descriptive benchmark comparison: PASS
- Non-mutating asset/FX scenario analysis: PASS
- Semantic D8 desktop accounting/analytics services: PASS
- Rust profile-mutation ownership and Python mutation locking: PASS
- First-class Portfolio Lab operation/inspection UI: PASS
- Responsive/keyboard/accessibility behavior: PASS
- macOS ARM64 and Linux x86-64 validation coverage: PASS
- No recommendation/broker/live-order/real-capital/arbitrary-code path: PASS
- No mandatory paid-provider dependency: PASS

## Validation

Accepted implementation head before documentation closeout: `620e8c9cdae188ca55945689c849b73e743c008a`.

Hosted validation on that head:

- Quality run #1183: success
- Desktop Foundation run #319: success
- python-and-architecture: success
- OpenSpec: success
- secret scan: success
- contributor rehearsal on macOS ARM64 and Linux x86-64: success
- package lifecycle on macOS ARM64 and Linux x86-64: success
- python-desktop-api: success
- frontend: success
- rust-broker: success
- linux-x86_64 desktop package smoke: success

The companion `validation-evidence.md` records the full manual acceptance outcome and the two UI findings fixed during acceptance.

## Naming follow-up resolution

The D7 follow-up concerning milestone-labelled modules under `src/osca/desktop_api` was reviewed during D8. `d3_*` through `d7_service.py` remain an intentional transitional compatibility inheritance ladder. D8 stops extending that naming pattern and introduces semantic `portfolio_accounting.py` and `portfolio_analytics.py` services instead. A broad rename remains deferred to a focused compatibility refactor because it is not required for D8 correctness and would increase regression risk.

## Remaining boundaries

D8 intentionally does not add selectable tax-accounting disposal policies such as FIFO/LIFO/average cost. Multi-lot disposals require explicit allocation instead of silently choosing a policy. D8 also does not introduce broker connectivity, live execution, personalized recommendations, autonomous capital actions, or arbitrary user code.
