# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P15 delivered provider governance, deterministic local research, model previews, narrow SEC/Kraken ingestion, personal-server operations, and governed trusted-local extensions. P16 completed the live-order readiness study and recorded ADR-0044: NO-GO. P17 remains blocked and is not authorized.

U8 reconciled the retained research workflow into the primary CLI. U9 added governed no-cost Kraken acquisition and fail-closed equity fallback. U10 added complete read-only research-evidence navigation and governed export. U11 provides one canonical first-run operator path. U12 now provides isolated wheel installation, release checksums/SBOM/provenance, compatibility inspection, verified backup and restore, and failed-upgrade recovery on macOS Apple Silicon and Linux x86-64.

Recommendations, live model serving, automatic promotion, brokers, autonomous execution, real-capital orders, untrusted extension execution, and a public extension marketplace remain disabled.

## Start here

1. [U11 canonical first-run quickstart](docs/milestones/u11/quickstart.md)
2. [U12 packaging and lifecycle status](docs/milestones/u12/README.md)
3. [U12 clean-machine acceptance](docs/milestones/u12/manual-acceptance.md)
4. [Manual testing and usage](docs/testing/manual-testing.md)
5. [Architecture status](ARCHITECTURE_STATUS.md)
6. [Product requirements](docs/product-requirements.md)
7. [Architecture decisions](docs/decisions/README.md)
8. [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
9. [U10 research-evidence workspace](docs/milestones/u10/README.md)
10. [Requirements catalog](docs/governance/requirements-catalog.md)

## Packaged installation

OSCA supports isolated installation from a verified wheel on macOS Apple Silicon and Linux x86-64:

```bash
uv tool install --force ./osca-<VERSION>-py3-none-any.whl
osca version
```

Before installation, verify the wheel against the distributed `SHA256SUMS`. Release artifacts also include a CycloneDX JSON SBOM and versioned provenance identifying the source commit, repository, package version, and artifact digests.

## Canonical first run

```bash
PROFILE_ROOT=".osca/profile"

osca init --profile-root "$PROFILE_ROOT"
osca doctor --profile-root "$PROFILE_ROOT"
```

Acquire governed no-cost Kraken history with explicit network opt-in:

```bash
osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --expected-pair-key XXBTZUSD \
  --minimum-rows 250 \
  --network-access-enabled \
  --storage-root "$PROFILE_ROOT/data"
```

Or import an offline CSV/Parquet dataset:

```bash
osca import-data \
  ./history.csv \
  AAPL \
  1d \
  --storage-root "$PROFILE_ROOT/data"
```

Run the retained experiment, diagnostic, and optional human-gated local-validation path:

```bash
osca research-pipeline \
  "$PROFILE_ROOT/data/payloads/<REVISION>.parquet" \
  "<REVISION>" \
  XBTUSD \
  1d \
  --storage-root "$PROFILE_ROOT/data" \
  --reviewer "$USER" \
  --rationale "Approved for local evidence-only research." \
  --approve-local-validation
```

Inspect the complete read-only evidence workspace:

```bash
osca workspace --profile-root "$PROFILE_ROOT" --snapshot
```

The generated profile is versioned and local. Network access is never implicit. The workspace remains loopback-only and read-only. Provider-restricted evidence is excluded from portable exports, and secrets or credentials are never placed in evidence bundles.

## Package lifecycle

```bash
osca lifecycle inspect --profile-root "$PROFILE_ROOT"
osca lifecycle backup \
  --profile-root "$PROFILE_ROOT" \
  --output ./osca-profile-backup.zip
osca lifecycle upgrade \
  --profile-root "$PROFILE_ROOT" \
  --backup ./osca-profile-backup.zip \
  --target-version <VERSION>
osca lifecycle restore \
  --backup ./osca-profile-backup.zip \
  --profile-root .osca/restored-profile
```

Lifecycle operations validate compatibility before mutation, require a verified backup before upgrade, reject unsafe archive paths, restore through staging and atomic replacement, and automatically recover from failed migration or post-upgrade validation.

## Canonical operator commands

- `osca init`: initialize safe versioned local configuration.
- `osca doctor`: diagnose runtime, storage, SQLite/Parquet, port, provider, credential, and evidence consistency.
- `osca historical-data fetch`: explicitly acquire admitted historical provider data.
- `osca import-data`: import governed local CSV or Parquet data.
- `osca analyze`: run deterministic local analysis.
- `osca backtest`: run built-in backtest-to-paper evidence.
- `osca research-pipeline`: run experiment, diagnostic, and optional human-gated local validation.
- `osca workspace`: snapshot or start the loopback-only read-only workspace.
- `osca version`: report installed package, runtime, platform, and build identity.
- `osca lifecycle inspect|backup|restore|upgrade`: manage the protected package/profile lifecycle.

The older command names remain compatibility entry points through U13 release-candidate acceptance.

## Current workflow

- P6-P8: import local OHLCV, generate deterministic research, and run backtest-to-paper evidence.
- P9-P10: use bounded SEC enrichment and explicit capability routing; FRED remains blocked.
- P11-P12: inspect retained evidence and optional deterministic/model-preview results through a loopback-only read-only workspace.
- P13: explicitly opt into bounded SEC or Kraken public-data ingestion with retained lineage.
- P14: run explicitly enabled personal-server jobs, alerts, backup, and restore operations.
- P15: validate, install, execute, inspect, and roll back independently trusted local extension packs.
- U5-U8: run classification experiments, prediction diagnostics, explicit human-gated validation, and one guided retained research pipeline.
- U9: acquire governed Kraken history or fail equity acquisition closed to CSV/Parquet fallback.
- U10: browse dedicated research evidence, inspect lineage, filter evidence, and create governed local exports.
- U11: initialize, diagnose, acquire/import, research, and inspect through one primary CLI.
- U12: install from a verified wheel and protect profiles through backup, upgrade, recovery, and restore.
- U13-U14: complete release-candidate acceptance and contributor readiness.

## Provider boundary

Kraken public spot OHLC is admitted for explicit internal-use acquisition. No no-cost equity provider currently passes the complete admission gate; equity requests fail closed and direct operators to governed CSV/Parquet import rather than silently calling an unapproved source.

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
