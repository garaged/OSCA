# D9 Traceability — Forward Paper Evaluation and Simulated Orders

| Authority / requirement | Implemented evidence |
|---|---|
| D-027, D-028 | `src/osca/paper/order_contracts.py`, `order_persistence.py`, `forward_service.py`; immutable simulated order/fill evidence and D8 journal posting |
| ADR-0046 | Python fill/risk/accounting authority in `src/osca/paper`; semantic desktop composition in `src/osca/desktop_api/paper_forward.py` and `paper_evaluation.py`; Rust retains profile-ownership/broker boundary only |
| REQ-0394 | retained M8 `PaperAccount` identity in `paper.sqlite`, `PaperRunBinding` in the D9 order store, `ForwardPaperService.bind_run`, desktop `paper.account.*` / `paper.run.bind`, and persistence/desktop tests proving arbitrary account UUIDs cannot bind |
| REQ-0395-0397 | immutable `SimulatedOrderDraft` versions, separate confirmation, order-type validation, retained lifecycle; fill-engine/service/desktop tests |
| REQ-0398-0400 | `fill_engine.py` point-in-time eligibility and conservative market/limit/stop/scheduled-market bar semantics; golden tests in `tests/paper/test_forward_fill_engine.py` |
| REQ-0401-0403 | explicit volume participation/partial fills plus retained spread, slippage, fees, latency and session/calendar evidence; fill-engine/service tests |
| REQ-0404-0405 | append-only lifecycle/idempotency, cancellation, expiry, rejection and replay-safe terminal behavior; persistence/service/recovery tests |
| REQ-0406 | pre-activation and pre-fill risk gates in `forward_service.py` plus retained M8 allow/pause/kill-switch decisions resolved server-side by `paper_evaluation.py`; blocked controls and insufficient cash/holdings/notional/exposure limits fail closed |
| REQ-0407 | replay-safe checkpoints, deterministic confirmation/order/fill/risk identities, process-restart replay and exact-once accounting tests in `test_forward_evidence_recovery.py` |
| REQ-0408 | D8 acquisition/disposal posting from retained fills plus explicit ambiguous-lot allocation; `forward_service.py` and service tests |
| REQ-0409 | `forward_evidence.py` retains completed-bar close as separate D8 valuation evidence with dataset/bar/source/effective/available provenance; missing evidence degrades/fails closed |
| REQ-0410 | local deterministic `process_bar` stepping and explicit governed-bar desktop input; no implicit provider/network fetch |
| REQ-0411 | `forward_comparison.py` and desktop comparison method retain distinct backtest/forward windows, assumption identity, methodology differences and Decimal deltas; descriptive/research-only |
| REQ-0412 | semantic `PaperForwardDesktopService` plus `PaperEvaluationDesktopService`, first-class `PaperForwardLabSurface`, typed `paperForwardApi.ts` / `paperAccountApi.ts`, responsive/accessibility CSS and frontend source-contract tests |
| REQ-0413 | `ProfileMutationLock` around Python D9 writes plus Rust `is_profile_mutation` ownership allow-list covering paper-account/control and order/run mutations; `d9_paper_writes_require_profile_ownership` test |
| REQ-0414 | Python/renderer result safety flags and source-contract tests prove no broker/exchange destination, credentials, provider fetch, live/real-capital execution, recommendation-to-order shortcut or arbitrary-code path |

## Validation state

Hosted Quality #1258 passed Ruff, strict mypy, the full tests/contracts/migrations/links/architecture suite, trusted-local extension conformance, OpenSpec and secret scanning on implementation head `1125933f321129f2068d9c61d25e9aa43a82d763`.

Desktop Foundation #352 passed the semantic Python desktop boundary, strict desktop mypy, desktop API/launcher tests, wheel sample verification, frontend build/tests, Rust formatting, Rust unit tests and Clippy on the same implementation head.

A final exact-head validation pass is required after this documentation/OpenSpec reconciliation. Manual supported-platform acceptance remains intentionally outstanding. `validation-evidence.md` and `exit-review.md` must not claim D9 PASS until that acceptance is recorded.
