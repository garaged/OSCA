# Specification - M5 Independent Extension Packaging and Activation

- **Status:** Accepted
- **Governing role:** Architecture authority
- **Requirements:** REQ-0069-REQ-0084
- **Related decisions:** D-019-D-020, D-040, D-046; ADR-0008, ADR-0030, ADR-0031
- **Risk class:** Security, reproducibility, compatibility, and extension lifecycle change
- **Last reviewed:** 2026-07-25

## Public contract families

- `osca.extension.manifest` 1.0.0 - accepted;
- `osca.extension.installation` 1.0.0 - accepted;
- `osca.extension.activation-decision` 1.0.0 - accepted;
- `osca.extension.impact-preview` 1.0.0 - accepted.

## Behavioral specification

Extension manifests declare exact identity, publisher, semantic version, category, entry points, OSCA compatibility, input/output/parameter schemas, supported asset classes and intervals, dependencies, permissions, determinism, resource requirements, integrity, license, provenance, and trust tier.

Manifest validation fails closed when package identity is missing, compatibility is empty, entry points are absent, dependencies or permissions are duplicated, integrity digest is missing, or semantic versions are malformed.

Installation records preserve the exact package identity, version, source, integrity digest, resolved dependencies, granted permissions, and activation state. Installing a newer package version creates a distinct installation record and must not reinterpret retained artifacts.

Extension installation records and activation decisions are persisted in SQLite metadata storage with stable identifiers and queryable lifecycle history.

Activation is an explicit decision. Untrusted or quarantined packages cannot activate until trust is raised by a governed approval. Permission changes require renewed approval before activation.

Disable and uninstall previews identify impacted retained analyses, artifacts, projects, reports, and dependent extensions before state changes are applied.

The CLI exposes metadata-only installation, activation decision, and installation-listing operations backed by the lifecycle store.

M5 does not execute third-party code. Runtime isolation, package loading, HTTP API/UI administration, registry distribution, strategy/backtest execution, ML, LLM, and paper trading remain deferred until governed separately.
