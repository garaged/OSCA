# Remaining P Milestone Roadmap

- **Status:** Active delivery roadmap
- **Governing role:** Product authority
- **Workflow:** One coherent branch and PR per meaningful milestone; continue autonomously unless a product, licensing, security, or architecture decision is required.
- **Completed through:** P14 personal-server production operations
- **Current milestone:** P15 governed runtime extension packs

## Current path

P5-P14 are complete. OSCA provides a deterministic local analyst workflow, optional model previews, narrowly admitted internal-use SEC/Kraken ingestion, and explicit trusted single-user operations.

P15 adds trusted local extension execution with exact integrity, compatibility, permissions, resource budgets, evidence, versioned installation, and rollback. It does not enable untrusted arbitrary code or a public marketplace.

## Milestone sequence

| Milestone | Objective | Status |
|---|---|---|
| P5-P8 | Operator visibility, local OHLCV, deterministic research, backtest-to-paper evidence | Complete |
| P9 | SEC fixture/live preview and FRED terms gate | Complete through PR #52 |
| P10 | Capability-based runtime routing | Complete through PR #53 |
| P11 | Read-only local analyst workspace | Complete through PR #54 |
| P12 | Optional local model-assisted previews | Complete through PR #55 |
| P13 | Evidence-gated SEC/Kraken internal-use production ingestion | Complete through PR #56 |
| P14 | Personal-server scheduling, alerts, backup/restore, packaging, and hardening | Complete through PR #57 |
| [P15](p15/README.md) | Governed trusted-local runtime extension packs | Implementation candidate in PR #58 |
| [P16](p16/README.md) | Real-money readiness threat model and explicit go/no-go ADR | Deferred; enables no orders |
| [P17](p17/README.md) | Tiny controlled live-order pilot only after explicit P16 approval | Not authorized |

## Capability assessment

- **Usable deterministic product:** P6-P11.
- **Optional enhancement:** P12 model-assisted previews and any future compliant macro provider.
- **Narrow internal-use production ingestion:** P13.
- **Personal-server operations:** P14.
- **Trusted local extensions:** P15 implementation candidate.
- **Not authorized:** real-capital execution.

## Boundary reminders

- Local/imported OHLCV remains the default no-cost path.
- SEC and Kraken production scopes remain narrow and internal-use only.
- Twelve Data, Alpha Vantage, and Nasdaq Data Link remain evidence-gated; FRED remains `policy_blocked`.
- P14 targets a trusted single-user host, not public multi-tenant SaaS.
- P15 executes only independently trusted local packs and is not a complete hostile-code sandbox.
- Public marketplaces, remote pack discovery, implicit permissions, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.
