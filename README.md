# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P8 provide a usable no-cost local evidence path: import user-supplied OHLCV, generate deterministic research observations, and run a transparent backtest into linked local paper evidence. P9 provides deterministic SEC fixture replay and explicit opt-in SEC EDGAR preview; FRED remains policy-blocked and optional. P10 provides capability-based routing with explicit selected, stale, unavailable, blocked, and partial outcomes. P11 provides a read-only local analyst workspace.

P12 is an optional implementation candidate. It adds deterministic zero-cost local trend inference and fixture-backed LLM analysis with budgets, exact model/prompt provenance, mandatory review, and fail-closed network/provider behavior. P12 is not required for the usable deterministic P6-P11 workflow. Production ingestion, paid provider promotion, remote model execution, recommendations, broker execution, autonomous trading, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [P8 milestone](docs/milestones/p8/README.md)
6. [P9 milestone](docs/milestones/p9/README.md)
7. [P10 milestone](docs/milestones/p10/README.md)
8. [P11 milestone](docs/milestones/p11/README.md)
9. [P12 milestone](docs/milestones/p12/README.md)
10. [P12 user testing quickstart](docs/milestones/p12/user-testing-quickstart.md)
11. [P11-P12 requirements and traceability reconciliation](docs/governance/p11-p12-reconciliation.md)
12. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current local workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9: replay SEC fixtures or explicitly opt into bounded SEC preview; FRED remains blocked.
- P10: inspect capability-based source decisions and partial macro/non-macro behavior.
- P11: browse retained evidence through a loopback-only read-only workspace.
- P12: optionally run local model-assisted previews while retaining budgets, provenance, blocked states, and mandatory review.

## Capability boundary

- **OHLCV:** governed local Parquet payloads routed through P10.
- **Company facts and filings:** SEC fixture or explicit opt-in SEC live preview.
- **Macro series:** optional; FRED is policy-blocked and alternatives are unavailable until configured.
- **Workspace:** P11 displays retained evidence without mutation or advice.
- **Model-assisted preview:** P12 local inference is deterministic; LLM output is fixture-backed and review-required. No live executor is configured.
- **Product independence:** macro and model providers are optional and do not block the deterministic analyst workflow.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Product decision log](docs/decision-log.md)
- [Architecture decisions](docs/decisions/README.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability model](docs/governance/traceability-model.md)
- [P11-P12 reconciliation](docs/governance/p11-p12-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
