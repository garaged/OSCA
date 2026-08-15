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

Automated evidence is implemented, but final gate status remains open until temporary diagnostic lint/type scopes are removed and hosted CI passes on the final head. `validation-evidence.md` and `exit-review.md` must only claim completed gates after hosted CI and supported-platform manual acceptance actually pass.
