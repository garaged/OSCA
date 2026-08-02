# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P15 delivered provider governance, deterministic local research, model previews, narrow SEC/Kraken ingestion, personal-server operations, and governed trusted-local extensions. P16 completed the live-order readiness study and recorded ADR-0044: NO-GO. P17 remains blocked and is not authorized.

U8 reconciled the real-world research workflow into the primary CLI and retained experiment, diagnostic, validation, and manifest evidence under governed storage. U9 is the next implementation milestone: governed no-cost historical-data acquisition. The approved U9-U14 path now focuses on data acquisition, workspace usability, first-run integration, packaging, release acceptance, and contributor readiness rather than additional analytical breadth.

Recommendations, live model serving, automatic promotion, brokers, autonomous execution, real-capital orders, untrusted extension execution, and a public extension marketplace remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
6. [U9 governed historical acquisition](docs/milestones/u9/README.md)
7. [U8 real-world workflow reconciliation](docs/milestones/u8/README.md)
8. [P milestone disposition](docs/milestones/remaining-p-roadmap.md)
9. [Requirements catalog](docs/governance/requirements-catalog.md)

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11: inspect retained evidence through a loopback-only read-only workspace.
- P12: optionally run deterministic local inference or fixture-backed review-required LLM previews.
- P13: explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.
- P14: run explicitly enabled personal-server jobs, alerts, backup, and restore operations.
- P15: validate, install, execute, inspect, and roll back independently trusted local extension packs.
- U5-U8: run classification experiments, prediction diagnostics, explicit human-gated validation, and one guided retained research pipeline.
- U9-U14: complete the path to a no-cost, clean-machine, evidence-complete release candidate.

## Next milestone

U9 adds a provider-neutral historical-acquisition capability through the primary `osca` CLI. It must preserve provider capability, licensing, attribution, quota, provenance, canonical revision, quality, security, and evidence controls. Kraken is the approved cryptocurrency path. A no-cost equity source may be admitted only after exact current terms, account, quota, historical-depth, adjustment, retention, export, backup, redistribution, and attribution evidence passes the provider admission gate. Local CSV import remains the provider-independent offline fallback.

See:

- [U9 milestone intent](docs/milestones/u9/README.md)
- [U9 OpenSpec proposal](openspec/changes/u9-governed-historical-acquisition/proposal.md)
- [U9 OpenSpec design](openspec/changes/u9-governed-historical-acquisition/design.md)
- [U9 implementation tasks](openspec/changes/u9-governed-historical-acquisition/tasks.md)

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
- [P milestone disposition](docs/milestones/remaining-p-roadmap.md)
- [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
