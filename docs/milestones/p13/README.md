# P13 - Production Provider Promotion and Ingestion

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Promote eligible providers through P1 evidence gates and implement production ingestion jobs only for providers with accepted licensing, quota, credential, and redistribution evidence.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p13-production-provider-promotion-ingestion.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p13-production-provider-promotion-ingestion/spec.md)

## Objective

Promote eligible providers through P1 evidence gates and implement production ingestion jobs only for providers with accepted licensing, quota, credential, and redistribution evidence.

## User-visible value

OSCA can ingest governed provider data without relying on fixtures or manual imports.

## Implementation scope

- Re-evaluate Twelve Data, Kraken, Alpha Vantage, Nasdaq Data Link, SEC, and FRED evidence.
- Enable credentials by named secret reference only.
- Add durable ingestion jobs with retries, rate limits, cache, lineage, and quality findings.
- Keep promotion decisions auditable and reversible.

## Explicit non-scope

- Real-capital execution, unsupported/unofficial provider APIs.

## Acceptance criteria

- REQ-0247-REQ-0253 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P1 gates, P5, P10.

## Risks and decisions

Licensing/account-plan evidence may block or narrow scope.
