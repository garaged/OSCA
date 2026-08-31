# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P15 delivered provider governance, deterministic local research, model previews, narrow SEC/Kraken ingestion, personal-server operations, and governed trusted-local extensions. P16 completed the live-order readiness study and recorded ADR-0044: NO-GO. P17 remains blocked and is not authorized.

U8 reconciled the retained research workflow into the primary CLI. U9 added governed no-cost Kraken acquisition and fail-closed equity fallback. U10 added complete read-only research-evidence navigation and governed export. U11 provides one canonical first-run operator path. U12 provides isolated wheel installation, release checksums/SBOM/provenance, compatibility inspection, verified backup and restore, and failed-upgrade recovery. U13 accepted and tagged `v0.1.0rc1`. U14 adds reproducible contributor validation and strict non-importing trusted-local extension conformance.

The desktop-product path is complete through D9 and D10 is implementing a first-class ML Lab for immutable governed datasets, versioned features/labels, bounded local experiments, chronological validation, mandatory baselines, and retained reproducibility evidence. Model approval, explainability, and drift remain D11 scope.

Recommendations, live model serving, automatic promotion, brokers, autonomous execution, real-capital orders, untrusted extension execution, remote extension installation, automatic extension updates, and a public extension marketplace remain disabled.

## Start here

1. [Desktop menu and recommended workflow guide](docs/product/desktop-user-guide.md)
2. [U11 canonical first-run quickstart](docs/milestones/u11/quickstart.md)
3. [U12 packaging and lifecycle status](docs/milestones/u12/README.md)
4. [U13 release-candidate notes](docs/milestones/u13/release-notes.md)
5. [U14 contributor and extension readiness](docs/milestones/u14/README.md)
6. [Contributor guide](CONTRIBUTING.md)
7. [Trusted-local extension development](docs/contributing/extension-development.md)
8. [Manual testing and usage](docs/testing/manual-testing.md)
9. [Architecture status](ARCHITECTURE_STATUS.md)
10. [Product requirements](docs/product-requirements.md)
11. [Architecture decisions](docs/decisions/README.md)
12. [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
13. [Requirements catalog](docs/governance/requirements-catalog.md)

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

## Contributor workflow

Supported contributor environments are macOS Apple Silicon and Linux x86-64 with Python 3.13, `uv`, Node.js 22, and npm.

```bash
uv sync --locked
npm ci --ignore-scripts
uv run python scripts/contributor_check.py
```

The canonical command runs formatting/lint checks, strict typing, tests and architecture checks, OpenSpec validation, and trusted-local extension conformance.

## Trusted-local extension conformance

```bash
uv run osca extension validate \
  --manifest examples/extensions/offline-mean/osca-extension.json
```

Validation is JSON-only and does not import or execute extension code. It verifies the versioned manifest, API compatibility, deprecation status, capabilities, provenance, SPDX license, contained artifact paths, and SHA-256 digests. A passing result does not authorize execution; independent trusted-local review remains required.

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
- `osca extension validate`: validate trusted-local extension structure and artifact integrity without code import.

The older command names remain compatibility entry points through the `0.1.x` release family unless a later accepted deprecation decision changes that support window.

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
- U13: retain the official 16-area RC acceptance result for `0.1.0rc1`.
- U14: bootstrap contributors and validate trusted-local extension packages without importing code.

## Provider boundary

Kraken public spot OHLC is admitted for explicit internal-use acquisition. No no-cost equity provider currently passes the complete admission gate; equity requests fail closed and direct operators to governed CSV/Parquet import rather than silently calling an unapproved source.

## Extension boundary

- **Trust:** only `built_in`, `verified`, or independently accepted `local_trusted` packs may execute.
- **Conformance:** U14 manifests must declare identity, API, capabilities, provenance, license, trust, and artifact digests.
- **Integrity:** the direct executable must match the manifest SHA-256 digest.
- **Compatibility:** API `1.x` is supported; API `0.9` is temporarily deprecated through `0.1.x`; unknown versions fail closed.
- **Permissions:** the approved set must exactly match the manifest set; changes require renewed approval.
- **Execution:** explicit enablement, direct subprocess, no shell, bounded timeout/output, minimized environment, JSON-object output.
- **Evidence:** package/version, permissions, logs, output digest, exit code, rationale, and findings are retained.
- **Rollback:** only to an already installed and revalidated version.
- **Distribution:** public marketplaces, remote installation, and automatic updates remain unavailable.
- **Sandbox:** subprocess isolation is not a complete hostile-code sandbox; untrusted execution remains unavailable.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [P milestone disposition](docs/milestones/remaining-p-roadmap.md)
- [U9-U14 usable release roadmap](docs/milestones/usable-release-roadmap.md)
- [Architecture registry](engineering/architecture-registry.yaml)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.
