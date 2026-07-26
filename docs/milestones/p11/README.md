# P11 - Useful Analyst Workspace

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Add a focused analyst workspace for projects, datasets, reports, backtests, and enrichment evidence.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p11-analyst-workspace.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p11-analyst-workspace/spec.md)

## Objective

Add a focused analyst workspace for projects, datasets, reports, backtests, and enrichment evidence.

## User-visible value

Users can browse and inspect OSCA output without reading raw metadata tables.

## Implementation scope

- Add a minimal local web/API-backed workspace or equivalent product UI.
- Show projects, watchlists, imported datasets, data quality, reports, backtests, and enrichment evidence.
- Add empty/error/loading states and manual smoke tests.

## Explicit non-scope

- Full BI platform, multi-user SaaS, extension marketplace UI.

## Acceptance criteria

- REQ-0233-REQ-0239 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P7-P10.

## Risks and decisions

UI scope can sprawl; P11 must stay read-mostly and evidence-oriented.
