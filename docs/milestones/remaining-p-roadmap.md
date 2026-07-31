# Remaining P Milestone Roadmap

- **Status:** Active delivery roadmap
- **Governing role:** Product authority
- **Workflow:** One coherent branch and PR per meaningful milestone; continue autonomously unless a product, licensing, security, or architecture decision is required.
- **Completed through:** P11 read-only analyst workspace
- **Current optional milestone:** P12 local model-assisted preview

## Current path

P5-P11 are complete. OSCA can import local OHLCV, generate deterministic research, run a transparent backtest into local paper evidence, replay or preview SEC evidence, route capabilities with explicit provenance, and expose retained results through a read-only local workspace.

P12 is optional. It adds deterministic local inference and fixture-backed LLM analysis, but the product remains usable without any model provider. FRED and model providers are not platform dependencies.

## Milestone sequence

| Milestone | Objective | Status |
|---|---|---|
| P5-P8 | Operator visibility, local OHLCV, deterministic research, backtest-to-paper evidence | Complete |
| P9 | SEC fixture/live preview and FRED terms gate | Complete through PR #52 |
| P10 | Capability-based runtime routing | Complete through PR #53 |
| P11 | Read-only local analyst workspace | Complete through PR #54 |
| [P12](p12/README.md) | Optional local model-assisted previews with budgets, provenance, review, and fail-closed controls | Implementation candidate in PR #55 |
| [P13](p13/README.md) | Evidence-gated production provider ingestion | Deferred pending exact evidence; FRED is not assumed |
| [P14](p14/README.md) | Personal-server scheduling, alerts, backup/restore, packaging, and hardening | Deferred |
| [P15](p15/README.md) | Governed runtime extension packs | Deferred |
| [P16](p16/README.md) | Real-money readiness threat model and explicit go/no-go ADR | Deferred; enables no orders |
| [P17](p17/README.md) | Tiny controlled live-order pilot only after explicit P16 approval | Not authorized |

## Capability assessment

- **Usable deterministic product:** P6-P11.
- **Optional enhancement:** P12 model-assisted previews and any future compliant macro provider.
- **Evidence-gated production work:** P13-P15.
- **Not authorized:** real-capital execution.

## Boundary reminders

- Local/imported OHLCV remains the default no-cost market-history path.
- SEC supplies company enrichment, not OHLCV or macro data.
- FRED remains `policy_blocked`.
- P11 remains read-only.
- P12 fixture LLM output is untrusted until reviewed; live model execution remains unavailable.
- Production ingestion, paid-provider promotion, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.
