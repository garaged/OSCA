# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P11 provide a usable deterministic local analyst workflow: governed OHLCV import, research, backtest-to-paper evidence, SEC preview, capability routing, and a read-only workspace. P12 adds optional local model-assisted previews with fail-closed live-model behavior.

P13 is the current implementation candidate. It adds evidence-gated production admission and durable internal-use ingestion for narrowly approved SEC EDGAR and Kraken public-data resources. Twelve Data, Alpha Vantage, and Nasdaq Data Link remain `needs_evidence`; FRED remains `policy_blocked`. Redistribution, paid-provider promotion without exact evidence, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [P11 milestone](docs/milestones/p11/README.md)
6. [P12 milestone](docs/milestones/p12/README.md)
7. [P13 milestone](docs/milestones/p13/README.md)
8. [P13 user testing quickstart](docs/milestones/p13/user-testing-quickstart.md)
9. [P12-P13 requirements reconciliation](docs/governance/p12-p13-reconciliation.md)
10. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11: inspect retained evidence through a loopback-only read-only workspace.
- P12: optionally run deterministic local inference or fixture-backed review-required LLM previews.
- P13: inspect provider admission, then explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.

## Capability boundary

- **Local OHLCV:** governed import and routing remain the default no-cost path.
- **SEC:** company facts/submissions may be ingested from official endpoints with a declared user agent.
- **Kraken:** public spot OHLC may be ingested for personal/internal use.
- **Other production providers:** unavailable until exact account-plan and dataset evidence is accepted.
- **Macro:** FRED remains policy-blocked and optional.
- **Model assistance:** optional; no live executor is configured.
- **Execution:** no recommendations, brokers, autonomous trading, or real-capital orders.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [P12-P13 reconciliation](docs/governance/p12-p13-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
