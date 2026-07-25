# Specification - M6 Backtesting and Strategy Validation Foundation

- **Status:** Proposed
- **Governing role:** Architecture authority
- **Requirements:** REQ-0085-REQ-0092
- **Related decisions:** D-004, D-009, D-021, D-027-D-028, D-037, D-041, D-046; ADR-0032
- **Risk class:** Financial correctness, reproducibility, and simulation semantics
- **Last reviewed:** 2026-07-25

## Public contract families

- `osca.backtest.request` 1.0.0 - proposed;
- `osca.backtest.execution-plan` 1.0.0 - proposed;
- `osca.backtest.order-intent` 1.0.0 - proposed;
- `osca.backtest.result` 1.0.0 - proposed.

## Behavioral specification

Backtest requests declare project identity, strategy identity, fidelity profile, execution mode, bounded timezone-aware window, pinned dataset revisions, data availability, assumptions, and optional random seed.

Fidelity profiles distinguish F0 signal study, F1 vectorized portfolio estimate, F2 event-driven bar simulation, and F3 forward-paper evaluation. Execution planning requires each profile to use the compatible execution mode.

Backtest planning fails closed when inputs use revised-after-fact data, when event-driven or forward-paper profiles receive provisional data, or when F3 forward-paper behavior is requested before paper-account authority exists.

Strategy decisions retain evidence linkage and may produce order intents for simulated execution. Order intents are not live orders and do not imply brokerage or exchange execution.

Backtest execution plans disclose required checks and cannot be executable when error findings exist.

Completed backtest results retain typed metrics and methodology metadata. Unsupported behavior must be disclosed rather than approximated silently.

M6.1 does not implement event matching, fills, portfolio accounting, paper journals, runtime strategy execution, ML, LLM, or live execution.
