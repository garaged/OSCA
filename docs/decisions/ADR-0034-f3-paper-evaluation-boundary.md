# ADR-0034: F3 Paper Evaluation Boundary

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Architecture authority, product authority
- **Related requirements:** REQ-0102-REQ-0111
- **Related decisions:** D-001, D-002, D-027, D-028, D-036, D-037, D-041, D-046
- **Milestone:** M8

## Context

M7 established authoritative F2 historical validation evidence and explicit promotion gates. M8 must allow approved candidates to operate against forward market data in paper accounts while preserving the initial product boundary: no live brokerage orders, no real capital, deterministic risk authority, and no silent replay after restart.

Paper evaluation exercises order lifecycle, accounting, health, scheduling, alerts, and outcome learning in a forward setting. It must be isolated from research projects and from live execution adapters.

## Decision

M8 represents F3 as a separate paper-evaluation capability rooted in approved F2 promotion gates.

The first M8 boundary defines:

- independent paper account identity and lifecycle state;
- approved-candidate references derived from M7 promotion gates;
- paper evaluation requests scoped to one paper account, one approved candidate, and explicit data requirements;
- data and operational health gates that can block forward evaluation before order processing;
- account pause and system kill-switch state as deterministic controls;
- backtest-versus-forward comparison records that preserve metric methodology and findings.

Paper evaluation contracts may reference M7 F2 evidence but do not mutate it. F3 paper state is synthetic, local, and governed; it cannot route to broker or exchange live-order APIs.

## Consequences

- A clean F2 gate is necessary but not sufficient to run paper evaluation.
- F3 paper accounts are independent from research projects and are not mutable balance snapshots.
- Health gates, pause state, and kill switch become first-class evidence before durable automation is introduced.
- Durable market-aware scheduling, notification delivery, non-replay recovery, and SQLite persistence can be added in later M8 slices behind these contracts.
- Live execution remains out of scope and absent from interfaces.
