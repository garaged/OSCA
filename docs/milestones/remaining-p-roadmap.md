# Remaining P Milestone Roadmap

- **Status:** Active delivery roadmap
- **Governing role:** Product authority
- **Purpose:** Move OSCA from its governed foundation to a usable local analyst workflow, a production-capable personal service, and real-money readiness only if explicitly approved.
- **Workflow:** One coherent branch and PR per meaningful milestone by default; batch foreseeable decisions early; continue implementation without asking unless a product, legal/licensing, security, or architecture decision is required.
- **Completed through:** P9 SEC preview and FRED terms gate
- **Current milestone:** P10 capability-based runtime provider routing

## Shortest responsible path

P5-P9 are complete. OSCA can import user-supplied OHLCV, generate deterministic research evidence, run a transparent backtest into local paper evidence, replay SEC fixtures, and optionally use bounded SEC live preview. P10 creates one explicit source-decision surface; P11 will make the resulting projects, datasets, reports, backtests, and enrichment evidence approachable through a workspace.

FRED is optional. Its absence removes automatic macro-series enrichment only; it does not block OHLCV, SEC company facts/filings, research, backtesting, evidence retention, routing, or the analyst workspace.

## Milestone sequence

| Milestone | Phase | Objective | User-visible value | Status / dependencies |
|---|---|---|---|---|
| [P5](p5/README.md) | Minimum usable local/demo tool | Reconcile foundation/provider state and expose operator surfaces. | Maintainers can distinguish implemented, fixture-backed, specified-only, and deferred behavior. | Complete. |
| [P6](p6/README.md) | Minimum usable local/demo tool | Add governed local CSV/Parquet OHLCV import. | Users can run OSCA with their own data and no provider spend. | Complete. |
| [P7](p7/README.md) | Minimum usable local/demo tool | Produce deterministic research reports from imported data. | Users obtain useful local market observations. | Complete. |
| [P8](p8/README.md) | Useful analyst workflow | Move one transparent strategy through backtest and paper-evidence records. | Users compare a hypothesis with history and retain evidence. | Complete; manual evidence retained. |
| [P9](p9/README.md) | Useful analyst workflow | Add safe SEC fixture/live preview and retain the FRED terms gate. | Analysts can use official SEC enrichment while FRED fails closed. | Complete through PR #52. |
| [P10](p10/README.md) | Useful analyst workflow | Route supported capabilities across explicit governed local and SEC sources with stale, blocked, unavailable, and partial outcomes. | Users see the selected source or exact reason none can be selected; macro blocks do not stop non-macro work. | Implementation candidate in PR #53; depends on P6 and P9. |
| [P11](p11/README.md) | Useful analyst workflow | Add a focused analyst workspace for projects, datasets, reports, backtests, routing decisions, and enrichment evidence. | Users browse and inspect OSCA output without moving raw payload paths manually. | Planned; depends on P7-P10. |
| [P12](p12/README.md) | Useful analyst workflow | Turn governed ML and LLM lifecycle contracts into opt-in local previews with budgets and provenance. | Users can experiment with model-assisted analysis while preserving cost/privacy/evidence boundaries. | Optional after P11. |
| [P13](p13/README.md) | Production-capable version | Promote eligible providers and implement ingestion only with accepted licensing, quota, credential, retention, export, and redistribution evidence. | OSCA can ingest governed provider data without manual imports. | Deferred pending exact evidence; FRED is not assumed. |
| [P14](p14/README.md) | Production-capable version | Add personal-server scheduling, alerts, backup transport, restore execution, packaging, and security hardening. | OSCA can operate as a durable personal service. | Deferred until P10-P13. |
| [P15](p15/README.md) | Production-capable version | Execute trusted provider, analysis, and visualization packs through governed extension controls. | Users can extend OSCA without modifying core. | Deferred until P11-P14. |
| [P16](p16/README.md) | Real-money readiness | Produce threat models, controls, and an explicit go/no-go ADR. | Prevents accidental drift into capital execution. | Deferred; does not enable orders. |
| [P17](p17/README.md) | Real-money readiness | Only if P16 approves, implement a tiny controlled live-order pilot. | Tests execution mechanics under strict limits. | Not authorized. |

## Capability assessment

- **Usable now:** local OHLCV import, deterministic research, transparent backtesting, buy-and-hold comparison, local paper evidence, SEC fixture replay, and optional SEC preview.
- **P10 contribution:** coherent capability routing and explicit source/status provenance.
- **Required for approachable product use:** P11 analyst workspace.
- **Optional:** FRED or another macro provider, P12 model-assisted previews.
- **Evidence-gated:** P13-P15 production providers and operations.
- **Not authorized:** P16-P17 real-capital execution unless separately approved.

## Boundary reminders

- Local/imported OHLCV is the default no-cost market-history path.
- SEC supplies company enrichment; it is not an OHLCV or macro substitute.
- FRED requests remain `policy_blocked`; an unconfigured macro source is `provider_unavailable`.
- A macro block must not fail successful non-macro routing decisions.
- Runtime routing never silently blends or discovers sources.
- Production ingestion, paid provider promotion, recommendations, broker execution, autonomous trading, and real-capital orders remain disabled until explicitly owned and approved.
