# P10 - Runtime Provider Routing

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Introduce governed runtime routing across local imports, fixtures, and approved enrichment adapters with explicit policy-blocked and stale states.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p10-runtime-provider-routing.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p10-runtime-provider-routing/spec.md)

## Objective

Introduce governed runtime routing across local imports, fixtures, and approved enrichment adapters with explicit policy-blocked and stale states.

## User-visible value

Users can request data or enrichment through one product surface and understand which source was used or blocked.

## Implementation scope

- Define routing policy and source precedence.
- Route local OHLCV, fixtures, SEC EDGAR, and FRED preview sources where enabled.
- Record source selection, stale data, partial results, and policy blocks.
- Add API/CLI inspection for routing decisions.

## Explicit non-scope

- Production promotion of paid providers, real-time streaming, trading orders.

## Acceptance criteria

- REQ-0226-REQ-0232 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P6 and P9.

## Risks and decisions

Routing must not silently blend sources or bypass provider/legal gates.
