# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P11 provide a usable deterministic local analyst workflow. P12 adds optional local model-assisted previews. P13 adds narrowly admitted internal-use SEC EDGAR and Kraken ingestion. P14 adds explicit single-user personal-server operations.

P15 is the current implementation candidate. It adds trusted local runtime extension packs with exact integrity, compatibility, permission, resource, evidence, installation, and rollback controls. Packs execute as direct subprocesses rather than in-process imports. Execution is disabled by default. Public marketplaces, untrusted execution, provider expansion, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [P14 milestone](docs/milestones/p14/README.md)
6. [P15 milestone](docs/milestones/p15/README.md)
7. [P15 user testing quickstart](docs/milestones/p15/user-testing-quickstart.md)
8. [P14-P15 requirements reconciliation](docs/governance/p14-p15-reconciliation.md)
9. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11: inspect retained evidence through a loopback-only read-only workspace.
- P12: optionally run deterministic local inference or fixture-backed review-required LLM previews.
- P13: explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.
- P14: run explicitly enabled personal-server jobs, alerts, backup, and restore operations.
- P15: validate, install, execute, inspect, and roll back independently trusted local extension packs.

## Extension boundary

- **Trust:** only `built_in`, `verified`, or independently accepted `local_trusted` packs may execute.
- **Integrity:** the direct executable must match the manifest SHA-256 digest.
- **Compatibility:** the declared minimum OSCA version must be satisfied.
- **Permissions:** the approved set must exactly match the manifest set; changes require renewed approval.
- **Execution:** explicit enablement, direct subprocess, no shell, bounded timeout/output, minimized environment, JSON-object output.
- **Evidence:** package/version, permissions, logs, output digest, exit code, rationale, and findings are retained.
- **Rollback:** only to an already installed and revalidated version.
- **Sandbox:** subprocess isolation is not a complete hostile-code sandbox; untrusted execution remains unavailable.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [P14-P15 reconciliation](docs/governance/p14-p15-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
