# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P8 provide a usable no-cost local evidence path: import user-supplied OHLCV, generate deterministic research observations, and run a transparent backtest into a linked local paper-evaluation record. P9 provides deterministic SEC fixture replay and explicit opt-in SEC EDGAR preview; FRED remains policy-blocked and optional. P10 provides capability-based routing with explicit selected, stale, unavailable, blocked, and partial outcomes.

P11 is the current implementation candidate. It adds a focused read-only local browser/API workspace for projects, watchlists, datasets, reports, backtests, SEC evidence, and P10 routing decisions. Production ingestion, paid provider promotion, recommendations, broker execution, autonomous trading, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [M0 architecture overview](docs/architecture/README.md)
4. [M0.x operationalization](docs/milestones/m0x/README.md)
5. [Architecture handbook](docs/handbook/README.md)
6. [Architecture decisions](docs/decisions/README.md)
7. [Engineering constitution](engineering/constitution.md)
8. [Manual testing and usage](docs/testing/manual-testing.md)
9. [P8 milestone](docs/milestones/p8/README.md)
10. [P9 milestone](docs/milestones/p9/README.md)
11. [P10 milestone](docs/milestones/p10/README.md)
12. [P11 milestone](docs/milestones/p11/README.md)
13. [P11 user testing quickstart](docs/milestones/p11/user-testing-quickstart.md)
14. [P10-P11 requirements and traceability reconciliation](docs/governance/p10-p11-reconciliation.md)
15. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current local workflow

The P6-P8 walkthrough is documented in [P8 user testing quickstart](docs/milestones/p8/user-testing-quickstart.md). It imports `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv`, confirms `row_count: 10`, captures the emitted `payload_uri`, and uses that exact payload for research and backtest-to-paper evidence.

The P9 preview workflow is documented in [P9 user testing quickstart](docs/milestones/p9/user-testing-quickstart.md). Start with deterministic SEC fixture replay. SEC network access is optional and explicit; FRED live use remains blocked.

The P10 routing workflow is documented in [P10 user testing quickstart](docs/milestones/p10/user-testing-quickstart.md). It inspects the capability matrix, selects local OHLCV and SEC fixture evidence, confirms FRED's policy block, and demonstrates partial mixed-batch behavior.

The P11 workspace workflow is documented in [P11 user testing quickstart](docs/milestones/p11/user-testing-quickstart.md). It first inspects a JSON snapshot, then starts a loopback-only read-only browser/API workspace over the retained evidence root.

## Capability boundary

- **OHLCV:** governed local Parquet payloads routed through P10.
- **Company facts and filings:** SEC fixture or explicit opt-in SEC live preview.
- **Macro series:** optional; FRED is policy-blocked and an unconfigured alternative is provider-unavailable.
- **Workspace:** P11 displays retained evidence and routing status but does not create, edit, execute, or reinterpret it as advice.
- **Product independence:** the absence of a macro provider does not block research, backtesting, SEC enrichment, routing, or the analyst workspace.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Product decision log](docs/decision-log.md)
- [Architecture decisions](docs/decisions/README.md)
- [Document control](docs/governance/document-control.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability model](docs/governance/traceability-model.md)
- [P8-P9 reconciliation](docs/governance/p8-p9-reconciliation.md)
- [P9-P10 reconciliation](docs/governance/p9-p10-reconciliation.md)
- [P10-P11 reconciliation](docs/governance/p10-p11-reconciliation.md)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.

## Engineering system

- [Engineering constitution](engineering/constitution.md)
- [Decision matrix](engineering/decision-matrix.md)
- [AI contributor contract](engineering/ai-contributor-contract.md)
- [Architecture evolution policy](engineering/architecture-evolution-policy.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Engineering bootstrap](engineering/bootstrap/README.md)
- [OpenSpec integration policy](docs/governance/openspec-integration.md)
- [Architecture validation](docs/validation/README.md)
- [Manual testing and usage](docs/testing/manual-testing.md)
