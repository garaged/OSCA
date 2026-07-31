# Remaining P Milestone Roadmap

- **Status:** Active delivery roadmap
- **Governing role:** Product authority
- **Workflow:** One coherent branch and PR per meaningful milestone; continue autonomously unless a product, licensing, security, or architecture decision is required.
- **Completed through:** P13 governed production provider admission and ingestion
- **Current milestone:** P14 personal-server production operations

## Current path

P5-P13 are complete. OSCA provides a deterministic local analyst workflow, optional model previews, and narrowly admitted internal-use SEC/Kraken production ingestion with retained lineage.

P14 makes the single-user host operable through explicit scheduler execution, alerts, backup/restore, security validation, and hardened deployment examples. Every external or mutating action remains disabled by default.

## Milestone sequence

| Milestone | Objective | Status |
|---|---|---|
| P5-P8 | Operator visibility, local OHLCV, deterministic research, backtest-to-paper evidence | Complete |
| P9 | SEC fixture/live preview and FRED terms gate | Complete through PR #52 |
| P10 | Capability-based runtime routing | Complete through PR #53 |
| P11 | Read-only local analyst workspace | Complete through PR #54 |
| P12 | Optional local model-assisted previews | Complete through PR #55 |
| P13 | Evidence-gated SEC/Kraken internal-use production ingestion | Complete through PR #56 |
| [P14](p14/README.md) | Personal-server scheduling, alerts, backup/restore, packaging, and hardening | Implementation candidate in PR #57 |
| [P15](p15/README.md) | Governed runtime extension packs | Deferred until P14 |
| [P16](p16/README.md) | Real-money readiness threat model and explicit go/no-go ADR | Deferred; enables no orders |
| [P17](p17/README.md) | Tiny controlled live-order pilot only after explicit P16 approval | Not authorized |

## Capability assessment

- **Usable deterministic product:** P6-P11.
- **Optional enhancement:** P12 model-assisted previews and any future compliant macro provider.
- **Narrow internal-use production ingestion:** P13.
- **Personal-server operations:** P14 implementation candidate.
- **Future extension runtime:** P15.
- **Not authorized:** real-capital execution.

## Boundary reminders

- Local/imported OHLCV remains the default no-cost path.
- SEC and Kraken production scopes remain narrow and internal-use only.
- Twelve Data, Alpha Vantage, and Nasdaq Data Link remain evidence-gated; FRED remains `policy_blocked`.
- P14 targets a trusted single-user host, not public multi-tenant SaaS.
- TLS certificates, identities, firewalling, host patching, and off-device storage access remain operator-owned.
- Recommendations, brokers, autonomous execution, and real-capital orders remain disabled.
