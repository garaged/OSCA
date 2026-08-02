# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P15 delivered provider governance, deterministic local research, model previews, narrow SEC/Kraken ingestion, personal-server operations, and governed trusted-local extensions. P16 completed the live-order readiness study and recorded ADR-0044: NO-GO. P17 remains blocked and is not authorized.

U8 reconciled the real-world research workflow into the primary CLI. U9 now provides governed no-cost Kraken historical acquisition, explicit blocked-equity behavior with CSV fallback, canonical revisions, persisted lifecycle evidence, full degraded outcomes, U8 handoff, and complete recursive workspace discovery. U10 is the next milestone: dedicated research-evidence workspace sections and detail views.

Recommendations, live model serving, automatic promotion, brokers, autonomous execution, real-capital orders, untrusted extension execution, and a public extension marketplace remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [Architecture decisions](docs/decisions/README.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
6. [U9 governed historical acquisition](docs/milestones/u9/README.md)
7. [U9 exit review](docs/milestones/u9/exit-review.md)
8. [U9 traceability](docs/milestones/u9/traceability.md)
9. [U8 real-world workflow reconciliation](docs/milestones/u8/README.md)
10. [Requirements catalog](docs/governance/requirements-catalog.md)

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11: inspect retained evidence through a loopback-only read-only workspace.
- P12: optionally run deterministic local inference or fixture-backed review-required LLM previews.
- P13: explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.
- P14: run explicitly enabled personal-server jobs, alerts, backup, and restore operations.
- P15: validate, install, execute, inspect, and roll back independently trusted local extension packs.
- U5-U8: run classification experiments, prediction diagnostics, explicit human-gated validation, and one guided retained research pipeline.
- U9: acquire governed Kraken history or fail equity acquisition closed to CSV fallback; retain canonical, lifecycle, lineage, degraded-state, and workspace evidence.
- U10-U14: complete workspace usability, first-run integration, packaging, release acceptance, and contributor readiness.

## U9 historical acquisition

```bash
uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --expected-pair-key XXBTZUSD \
  --minimum-rows 250 \
  --network-access-enabled \
  --storage-root .osca/research
```

The command accepts timezone-aware ISO-8601 `--start-at` and `--end-at` values, retains request/job/correlation evidence, validates provider mapping, excludes Kraken's current uncommitted bar, creates a canonical Parquet/SQLite revision, and records raw/normalized digests and safety boundaries.

No no-cost equity provider currently passes the complete admission gate. Equity requests fail closed and direct users to governed CSV import rather than silently calling an unapproved source.

## Next milestone

U10 adds dedicated read-only workspace sections and detail views for:

- historical acquisitions and persisted jobs;
- datasets and lineage;
- ML experiments;
- prediction diagnostics;
- model validations;
- pipeline manifests and backtests;
- evidence digests, warnings, safety states, filtering, and portable export.

U10 must preserve U9 provider licensing, provenance, read-only, and no-execution boundaries.

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
- [P milestone disposition](docs/milestones/remaining-p-roadmap.md)
- [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
