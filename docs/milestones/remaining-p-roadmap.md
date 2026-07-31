# Remaining P Milestone Roadmap

- **Status:** Active delivery roadmap
- **Governing role:** Product authority
- **Purpose:** Define the remaining P milestone sequence needed to move OSCA from governed foundation to usable local/demo tool, useful analyst workflow, production-capable version, and real-money readiness only if explicitly approved.
- **Workflow:** One coherent branch and PR per meaningful milestone by default; batch foreseeable decisions early; continue implementation without asking unless a product, legal/licensing, security, or architecture decision is required.
- **Completed through:** P8 backtest-to-paper happy path
- **Current milestone:** P9 SEC preview and FRED terms gate

## Shortest responsible path

P5 through P8 are complete. OSCA now has a useful local evidence path from user-supplied OHLCV through deterministic research and backtest-to-paper evidence. The next practical analyst path is P9 enrichment preview, P10 governed source routing, and P11 an analyst workspace.

SEC EDGAR and FRED are enrichment sources, not market-price-history substitutes. P9 implements safe opt-in SEC preview. FRED live use remains policy-blocked until accepted licensing evidence permits OSCA's software use and retention model.

## Milestone sequence

| Milestone | Phase | Objective | User-visible value | Status / dependencies |
|---|---|---|---|---|
| [P5](p5/README.md) | Minimum usable local/demo tool | Reconcile M0-M12 and P1-P4 state and expose provider-governance operator surfaces. | Maintainers can distinguish implemented, fixture-backed, specified-only, and deferred provider behavior. | Complete. |
| [P6](p6/README.md) | Minimum usable local/demo tool | Add governed local CSV/Parquet OHLCV import. | Users can run OSCA with their own data and no provider spend. | Complete. |
| [P7](p7/README.md) | Minimum usable local/demo tool | Produce a deterministic research report from imported data. | Users can obtain useful local market observations. | Complete. |
| [P8](p8/README.md) | Useful analyst workflow | Move one transparent strategy from local data through backtest evidence into a paper-evaluation record. | Users can compare a hypothesis with historical data and retain evidence. | Complete; manual evidence retained. |
| [P9](p9/README.md) | Useful analyst workflow | Implement opt-in SEC EDGAR preview behind fail-closed network, fair-access, cache, and provenance controls; keep FRED live use behind a terms gate. | Analysts can replay SEC fixtures, explicitly preview official SEC enrichment, and receive a structured FRED policy block. | Implementation candidate; depends on P4-P8. |
| [P10](p10/README.md) | Production-capable foundation | Introduce governed runtime routing across local imports, fixtures, approved previews, and explicit policy-blocked/stale states. | Users can request data or enrichment through one surface and understand the selected or blocked source. | Planned; depends on P6 and P9. |
| [P11](p11/README.md) | Useful analyst workflow | Add a focused analyst workspace for projects, datasets, reports, backtests, and enrichment evidence. | Users can browse and inspect OSCA output without moving raw payload paths manually. | Planned; depends on P7-P10. |
| [P12](p12/README.md) | Useful analyst workflow | Turn governed ML and LLM lifecycle contracts into opt-in local previews with budgets, provenance, and fail-closed controls. | Users can experiment with model-assisted analysis while preserving cost/privacy/evidence boundaries. | Optional enhancement after P11. |
| [P13](p13/README.md) | Production-capable version | Promote eligible providers through P1 evidence gates and implement ingestion only with accepted licensing, quota, credential, retention, export, and redistribution evidence. | OSCA can ingest governed provider data without manual imports. | Deferred pending exact evidence. |
| [P14](p14/README.md) | Production-capable version | Add credible personal-server scheduling, alerts, backup transport, restore execution, packaging, and security hardening. | OSCA can operate as a durable personal service. | Deferred until P10-P13. |
| [P15](p15/README.md) | Production-capable version | Execute trusted provider, analysis, and visualization packs through governed extension controls. | Users can extend OSCA without modifying core. | Deferred until P11-P14. |
| [P16](p16/README.md) | Real-money/order-execution readiness | Produce threat models, controls, and an explicit go/no-go ADR for real-money execution. | Prevents accidental drift into capital execution. | Deferred; does not enable orders. |
| [P17](p17/README.md) | Real-money/order-execution readiness | Only if P16 explicitly approves, implement a tiny controlled live-order pilot with hard limits and manual approval. | Tests execution mechanics under strict controls. | Not authorized. |

## Practical local analyst delivery assessment

- **Usable now:** Local OHLCV import, deterministic research reporting, transparent backtesting, comparison with buy-and-hold, and local paper-evaluation evidence.
- **Required next:** P9, P10, and P11 provide enrichment, coherent source resolution, and an approachable analyst workspace.
- **Optional later:** P12 model-assisted previews are not required for a useful deterministic local tool.
- **Remain deferred:** P13-P15 require licensing/security/operations evidence; P16-P17 remain behind explicit product, legal, security, and financial-risk decisions.

## Boundary reminders

- Synthetic fixtures support deterministic development and tests.
- Local/imported OHLCV remains the default no-cost market-history path.
- SEC EDGAR preview is enrichment evidence, not OHLCV or financial advice.
- FRED live requests, key resolution, caching, and archival are policy-blocked in P9.
- Kraken Spot and Twelve Data remain governed production-promotion candidates.
- Alpha Vantage and Nasdaq Data Link remain conditional candidates.
- Stooq remains research-only.
- Unofficial Yahoo Finance paths remain excluded unless a compliant official API/license path is evidenced.
- Runtime routing, production ingestion, production promotion, broker execution, autonomous trading, and real-capital orders remain deferred until a milestone explicitly owns and passes their gates.
