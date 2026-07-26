# P9 SEC/FRED Live Preview Adapters Specification

## Purpose

Implement opt-in live preview adapters for official no-cost SEC EDGAR and FRED enrichment sources behind fail-closed network, fair-use, cache, and credential-reference gates.

## Phase

Useful analyst workflow

## User-visible value

Analysts can enrich local research with official filings and macro series when explicitly enabled.

## Requirements

- REQ-0219-REQ-0225: OSCA must implement the P9 scope described by this specification before P9 is marked complete.
- REQ-0219-REQ-0225: P9 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0219-REQ-0225: P9 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Add SEC EDGAR no-key client with declared user-agent and fair-access limits.
- Add FRED API-key-reference client without credential values in code or metadata.
- Add cache, throttling, fixtures, and replay tests.
- Keep adapters preview-only and disabled by default.

## Explicit non-scope

- OHLCV substitution, production promotion, paid provider calls.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P5-P7 and P4 adapter contracts.

## Risks and decisions

Provider terms and fair-access constraints must be rechecked before implementation.
