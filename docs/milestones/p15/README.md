# P15 - Runtime Extensions and Packs

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Allow trusted provider, analysis, and visualization packs to execute through governed extension lifecycle controls.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p15-runtime-extensions-packs.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p15-runtime-extensions-packs/spec.md)

## Objective

Allow trusted provider, analysis, and visualization packs to execute through governed extension lifecycle controls.

## User-visible value

Users can extend OSCA without modifying the core repository.

## Implementation scope

- Define runtime extension permission model.
- Load and execute trusted packs with versioning and rollback.
- Validate contracts, manifests, evidence, and compatibility.
- Add conformance tests for external packs.

## Explicit non-scope

- Public marketplace, untrusted arbitrary code execution.

## Acceptance criteria

- REQ-0261-REQ-0267 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

M5 and P11-P14.

## Risks and decisions

Sandboxing and permission renewal need an architecture decision before broad enablement.
