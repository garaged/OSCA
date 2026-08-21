# D9 Traceability — Forward Paper Evaluation and Simulated Orders

| Authority / requirement | Planned implementation evidence |
|---|---|
| D-027, D-028 | shared event-driven paper domain; immutable simulated order/fill events; D8 journal posting |
| ADR-0046 | Python fill/risk/accounting authority; typed desktop adapter; Rust profile ownership only |
| REQ-0394 | paper-account to D8-portfolio binding contracts/persistence/tests |
| REQ-0395-0397 | immutable order drafts/versions, confirmation, order-type validation tests |
| REQ-0398-0400 | point-in-time eligibility and deterministic market/limit/stop golden fill tests |
| REQ-0401-0403 | volume participation/partial fills, explicit assumptions, market-calendar and 24/7 tests |
| REQ-0404-0405 | append-only lifecycle/idempotency/cancel/expiry/rejection state-machine tests |
| REQ-0406 | deterministic pre-activation/pre-fill risk-gate tests |
| REQ-0407 | checkpoint/crash/restart/recovery and no-duplicate-fill tests |
| REQ-0408 | D8 acquisition/disposal posting and explicit ambiguous-lot allocation tests |
| REQ-0409-0411 | mark provenance/degraded evidence, local deterministic stepping, descriptive backtest comparison tests |
| REQ-0412 | semantic desktop paper-evaluation API and Paper Lab frontend/accessibility tests |
| REQ-0413 | Rust broker mutation allow-list + Python profile mutation lock tests |
| REQ-0414 | source/boundary tests proving absence of broker/exchange/live/real-capital/arbitrary-code paths |

This document records planned evidence while implementation is in progress. `validation-evidence.md` and `exit-review.md` will only be added after hosted CI and supported-platform manual acceptance pass.
