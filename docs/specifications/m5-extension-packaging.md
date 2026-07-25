# Specification - M5 Independent Extension Packaging and Activation

- **Status:** Draft
- **Governing role:** Architecture authority
- **Requirements:** REQ-0069-REQ-0084
- **Related decisions:** D-019-D-020, D-040, D-046; ADR-0008, ADR-0030, ADR-0031
- **Risk class:** Security, reproducibility, compatibility, and extension lifecycle change
- **Last reviewed:** 2026-07-24

## Public contract families

- `osca.extension.manifest` 1.0.0 - draft;
- `osca.extension.installation` 1.0.0 - draft;
- `osca.extension.activation-decision` 1.0.0 - draft;
- `osca.extension.impact-preview` 1.0.0 - draft.

## Behavioral specification

Extension manifests declare exact identity, publisher, semantic version, category, entry points, OSCA compatibility, input/output/parameter schemas, supported asset classes and intervals, dependencies, permissions, determinism, resource requirements, integrity, license, provenance, and trust tier.

Manifest validation fails closed when package identity is missing, compatibility is empty, entry points are absent, dependencies or permissions are duplicated, or integrity digest is missing.

Installation records preserve the exact package identity, version, source, integrity digest, resolved dependencies, granted permissions, and activation state. Installing a newer package version creates a distinct installation record and must not reinterpret retained artifacts.

Activation is an explicit decision. Untrusted or quarantined packages cannot activate until trust is raised by a governed approval. Permission changes require renewed approval before activation.

Disable and uninstall previews identify impacted retained analyses, artifacts, projects, reports, and dependent extensions before state changes are applied.

M5 does not execute third-party code. Runtime isolation, package loading, CLI/UI administration, registry distribution, strategy/backtest execution, ML, LLM, and paper trading remain deferred until governed separately.
