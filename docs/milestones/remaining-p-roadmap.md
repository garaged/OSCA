# Remaining P Milestone Roadmap

- **Status:** Planned
- **Governing role:** Product authority
- **Purpose:** Define the remaining P milestone sequence needed to move OSCA from governed foundation to usable local/demo tool, useful analyst workflow, production-capable version, and real-money readiness only if explicitly approved.
- **Workflow:** One coherent branch and PR per meaningful milestone by default; batch foreseeable decisions early; continue implementation without asking unless a product, legal/licensing, security, or architecture decision is required.
- **Next milestone:** P8 backtest-to-paper happy path

## Shortest responsible path

The shortest responsible path through the local/demo phase is P5, then P6, then P7, then P8. OSCA should become useful with local/imported no-cost OHLCV data before spending implementation effort on live providers. SEC EDGAR and FRED are valuable enrichment sources, but they do not replace market-price history.

## Milestone sequence

| Milestone | Phase | Objective | User-visible value | Dependencies |
|---|---|---|---|---|
| [P5](p5/README.md) | Minimum usable local/demo tool | Reconcile M0-M12 and P1-P4 documentation, specifications, traceability, and implementation boundaries, then expose the existing provider catalog and adapter-contract state through operator-facing CLI/API commands. | Maintainers can see exactly what is complete, specified, fixture-backed, deferred, and ready for the next implementation slice. | P1-P4 provider governance and completed M0-M12 roadmap. |
| [P6](p6/README.md) | Minimum usable local/demo tool | Add a governed local file import path for OHLCV history so OSCA can analyze real user-supplied data without paid providers. | Users can run OSCA locally with their own CSV or Parquet market data and no provider spend. | P5 reconciliation, M2 storage model, M3 temporal correctness. |
| [P7](p7/README.md) | Minimum usable local/demo tool | Connect imported or bundled data to a narrow analyst workflow that produces a deterministic research report. | A user can run one command or simple local flow and get useful market observations from OSCA. | P6 local OHLCV import. |
| [P8](p8/README.md) | Useful analyst workflow | Make one reproducible strategy travel from local data through backtest evidence into paper-evaluation records. | Users can compare a strategy hypothesis against historical data and retain paper-evaluation evidence. | P7 demo workflow, M6-M8 validation foundations. |
| [P9](p9/README.md) | Useful analyst workflow | Implement opt-in live preview adapters for official no-cost SEC EDGAR and FRED enrichment sources behind fail-closed network, fair-use, cache, and credential-reference gates. | Analysts can enrich local research with official filings and macro series when explicitly enabled. | P5-P7 and P4 adapter contracts. |
| [P10](p10/README.md) | Production-capable version | Introduce governed runtime routing across local imports, fixtures, and approved enrichment adapters with explicit policy-blocked and stale states. | Users can request data or enrichment through one product surface and understand which source was used or blocked. | P6 and P9. |
| [P11](p11/README.md) | Useful analyst workflow | Add a focused analyst workspace for projects, datasets, reports, backtests, and enrichment evidence. | Users can browse and inspect OSCA output without reading raw metadata tables. | P7-P10. |
| [P12](p12/README.md) | Useful analyst workflow | Turn governed ML and LLM lifecycle contracts into opt-in local runtime previews with budgets, provenance, and fail-closed controls. | Users can experiment with model-assisted analysis while retaining evidence and cost/privacy boundaries. | P7-P11 and M9-M10 contracts. |
| [P13](p13/README.md) | Production-capable version | Promote eligible providers through P1 evidence gates and implement production ingestion jobs only for providers with accepted licensing, quota, credential, and redistribution evidence. | OSCA can ingest governed provider data without relying on fixtures or manual imports. | P1 gates, P5, P10. |
| [P14](p14/README.md) | Production-capable version | Make personal-server operation credible with scheduler execution, external alerts, backup transport, restore execution, release packaging, and security hardening. | A user can operate OSCA as a durable local/personal service rather than a demo script. | P10-P13 and M12 contracts. |
| [P15](p15/README.md) | Production-capable version | Allow trusted provider, analysis, and visualization packs to execute through governed extension lifecycle controls. | Users can extend OSCA without modifying the core repository. | M5 and P11-P14. |
| [P16](p16/README.md) | Real-money/order-execution readiness | Decide whether OSCA should support real-money order execution by producing threat models, controls, and a go/no-go ADR. | The project avoids drifting into capital execution without explicit product, legal, and security acceptance. | P13-P14. |
| [P17](p17/README.md) | Real-money/order-execution readiness | If and only if P16 approves, implement a tiny controlled live-order pilot with hard limits, manual approval, reconciliation, and rollback. | OSCA can test live execution mechanics under strict safety controls. | P16 approval ADR, P14 production operations. |

## Boundary reminders

- Synthetic fixtures support deterministic development and tests.
- Local/imported OHLCV is the preferred no-cost path to a usable demo before live provider work.
- SEC EDGAR and FRED are preferred no-cost enrichment candidates, not OHLCV substitutes.
- Kraken Spot and Twelve Data remain governed production-promotion candidates.
- Alpha Vantage and Nasdaq Data Link remain conditional candidates.
- Stooq remains research-only.
- Unofficial Yahoo Finance paths remain excluded unless a compliant official API/license path is evidenced.
- Live provider calls, credentials, runtime routing, production ingestion, production provider promotion, and real-capital orders remain deferred until a milestone explicitly owns them.
