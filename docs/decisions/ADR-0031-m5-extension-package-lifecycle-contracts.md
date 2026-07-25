# ADR-0031 - M5 Extension Package Lifecycle Contracts

- **Status:** Draft
- **Date:** 2026-07-24
- **Decision owner:** Architecture authority
- **Related requirements:** REQ-0069-REQ-0084
- **Related decisions:** D-019, D-020, D-040, D-046
- **Related ADRs:** ADR-0008, ADR-0030

## Context

The approved product scope requires independently packaged extensions that can be imported, updated, disabled, and uninstalled without living in the OSCA application repository. M4 created internal extension-compatible research, analysis, and visualization contracts, but did not define package lifecycle semantics.

M5 needs enough lifecycle structure to preserve reproducibility and fail closed on trust or permission ambiguity before any runtime execution exists.

## Decision

M5 introduces explicit extension lifecycle contract families:

- `osca.extension.manifest` 1.0.0;
- `osca.extension.installation` 1.0.0;
- `osca.extension.activation-decision` 1.0.0;
- `osca.extension.impact-preview` 1.0.0.

Extension manifests declare identity, publisher, version, category, entry points, schemas, compatibility, dependencies, permissions, supported scopes, determinism, resource requirements, integrity, license, provenance, and trust tier.

Installation records preserve the exact manifest identity, version, source, digest, resolved dependencies, granted permissions, and activation state. Activation is a separate explicit decision. Untrusted or quarantined packages fail closed, and permission changes require renewed approval.

Disable and uninstall operations must first produce impact previews for retained analyses, artifacts, projects, reports, and dependent extensions.

Runtime isolation and third-party code execution remain deferred until the package lifecycle is accepted and evidenced.

## Consequences

OSCA can reason about extension packages and reproducibility before executing external code. Later runtime and interface work must conform to these records rather than inventing a parallel lifecycle.

The cost is that M5 initially validates and records package intent without dynamically loading capabilities.
