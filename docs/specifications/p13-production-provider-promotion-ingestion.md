# P13 Production Provider Promotion and Ingestion Specification

## Purpose

Promote eligible providers through P1 evidence gates and implement production ingestion jobs only for providers with accepted licensing, quota, credential, and redistribution evidence.

## Phase

Production-capable version

## User-visible value

OSCA can ingest governed provider data without relying on fixtures or manual imports.

## Requirements

- REQ-0247-REQ-0253: OSCA must implement the P13 scope described by this specification before P13 is marked complete.
- REQ-0247-REQ-0253: P13 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0247-REQ-0253: P13 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Re-evaluate Twelve Data, Kraken, Alpha Vantage, Nasdaq Data Link, SEC, and FRED evidence.
- Enable credentials by named secret reference only.
- Add durable ingestion jobs with retries, rate limits, cache, lineage, and quality findings.
- Keep promotion decisions auditable and reversible.

## Explicit non-scope

- Real-capital execution, unsupported/unofficial provider APIs.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P1 gates, P5, P10.

## Risks and decisions

Licensing/account-plan evidence may block or narrow scope.
