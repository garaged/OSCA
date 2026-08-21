# D8 Traceability — Virtual-Portfolio Accounting Foundation

| Authority / requirement | Implementation evidence |
|---|---|
| PRD §23.1-23.4; D-028 | `src/osca/paper/accounting.py`, `accounting_contracts.py`, `accounting_persistence.py`, accounting/replay tests |
| ADR-0046 | Python accounting/analytics authority; typed React adapters; Rust ownership only |
| REQ-0375-0376 | portfolio creation/listing, immutable starting-cash event, desktop protocol tests |
| REQ-0377-0379 | balanced `JournalTransaction`, Decimal-only authority, SQLite append-only triggers, precision/immutability tests |
| REQ-0380-0381 | deterministic replay, retained lots/book cost, explicit ambiguous-lot rejection/allocation tests |
| REQ-0382 | split/dividend/fork posting, stable source identity, duplicate-source/idempotency tests |
| REQ-0383-0385 | valuation provenance/degraded state, analytics snapshots, performance/drawdown, attribution, scenario and descriptive benchmark tests |
| REQ-0386 | non-destructive `clone_portfolio` / `reset_portfolio` lineage and replay tests |
| REQ-0387-0388 | digest-protected `PortfolioBundle`, atomic restore transaction, tamper/conflict rollback tests |
| REQ-0389 | `PortfolioAccountingDesktopService`, `PortfolioAnalyticsDesktopService`, Portfolio Lab, typed frontend clients and source-contract/accessibility tests |
| REQ-0390 | no network path in accounting/analytics services; explicit false safety flags; frontend tests reject direct fetch/WebSocket/broker-submit paths |
| REQ-0391-0392 | Python `ProfileMutationLock`, Rust broker mutation allow-list/tests, idempotent accounting schema initialization, M8 paper store left unchanged |
| REQ-0393 | semantic `portfolio_accounting.py` / `portfolio_analytics.py`; sidecar routes through semantic services; no `d8_service.py` added |

## Validation closure

D8 automated and manual evidence is complete. Exact-head implementation validation passed on `620e8c9cdae188ca55945689c849b73e743c008a` through Quality run #1183 and Desktop Foundation run #319, including supported macOS ARM64 and Linux x86-64 contributor/package coverage. The user completed the full supported-platform manual acceptance procedure successfully.

See `validation-evidence.md` for the retained gate/manual evidence and `exit-review.md` for the accepted D8 exit decision.
