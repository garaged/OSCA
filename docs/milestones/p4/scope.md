# P4 Scope

## In scope

- Provider adapter contract models for SEC EDGAR and FRED.
- Fixture-backed request and payload validation contracts.
- Deterministic services that derive contracts from P3 preferred profiles.
- Tests proving only SEC EDGAR and FRED are adapter-contract ready.
- Governance updates for requirements, traceability, ADRs, OpenSpec, and manual review.

## Out of scope

- Live HTTP clients.
- Real provider API calls.
- Credential value access or vault integration.
- Runtime market-data routing changes.
- Production provider promotion.
- External redistribution or export enablement.
