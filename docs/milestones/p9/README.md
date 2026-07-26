# P9 - SEC/FRED Live Preview Adapters

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Implement opt-in live preview adapters for official no-cost SEC EDGAR and FRED enrichment sources behind fail-closed network, fair-use, cache, and credential-reference gates.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p9-sec-fred-live-preview-adapters.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p9-sec-fred-live-preview-adapters/spec.md)

## Objective

Implement opt-in live preview adapters for official no-cost SEC EDGAR and FRED enrichment sources behind fail-closed network, fair-use, cache, and credential-reference gates.

## User-visible value

Analysts can enrich local research with official filings and macro series when explicitly enabled.

## Implementation scope

- Add SEC EDGAR no-key client with declared user-agent and fair-access limits.
- Add FRED API-key-reference client without credential values in code or metadata.
- Add cache, throttling, fixtures, and replay tests.
- Keep adapters preview-only and disabled by default.

## Explicit non-scope

- OHLCV substitution, production promotion, paid provider calls.

## Acceptance criteria

- REQ-0219-REQ-0225 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P5-P7 and P4 adapter contracts.

## Risks and decisions

Provider terms and fair-access constraints must be rechecked before implementation.
