# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P11 provide a usable deterministic local analyst workflow. P12 adds optional local model-assisted previews. P13 adds evidence-gated, internal-use production ingestion for narrowly approved SEC EDGAR and Kraken public-data resources.

P14 is the current implementation candidate. It adds explicit single-user personal-server operations: secure exposure validation, governed command execution, configured alerts, off-source backup creation, active staged restore, and hardened systemd templates. All operational actions remain disabled by default. Multi-tenant SaaS, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [P13 milestone](docs/milestones/p13/README.md)
6. [P14 milestone](docs/milestones/p14/README.md)
7. [P14 user testing quickstart](docs/milestones/p14/user-testing-quickstart.md)
8. [P13-P14 requirements reconciliation](docs/governance/p13-p14-reconciliation.md)
9. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11: inspect retained evidence through a loopback-only read-only workspace.
- P12: optionally run deterministic local inference or fixture-backed review-required LLM previews.
- P13: explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.
- P14: run explicitly enabled personal-server jobs, alerts, backup, and restore operations with retained evidence.

## Operations boundary

- **Default exposure:** loopback-only.
- **Protected remote exposure:** TLS and authentication are mandatory; firewall, certificates, identities, and host patching remain operator-owned.
- **Scheduler:** executes only locally configured, explicitly enabled commands.
- **Alerts:** file or HTTPS webhook only; webhook destinations are redacted in evidence.
- **Backup:** filesystem archive to a destination outside the source tree; off-device storage may be mounted there.
- **Restore:** validated temporary staging and explicit overwrite permission.
- **Packaging:** hardened systemd examples, not managed infrastructure automation.
- **Execution:** no recommendations, brokers, autonomous trading, or real-capital orders.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [P13-P14 reconciliation](docs/governance/p13-p14-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
