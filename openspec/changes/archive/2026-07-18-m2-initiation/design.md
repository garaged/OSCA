## Context

M1 provides secure interfaces, durable work, typed metadata, telemetry, audit, recovery, and engineering gates. M2 introduces provider-neutral financial identity, external untrusted/licensed data, canonical daily observations, persistent revisions, freshness, repair, quality, and cleanup. Planning must prevent symbols, provider payloads, or a convenient storage adapter from becoming silent architecture.

## Goals and non-goals

### Goals

- Select one demonstrable stock-and-crypto daily-data vertical slice.
- Create traceable proposed requirements and acceptance criteria.
- Define ownership, contract candidates, failure/security/licensing behavior, risks, and evidence.
- Gate provider and persistence selection on explicit evidence.
- Protect the M2/M3 boundary.

### Non-goals

- Approve requirements or providers through OpenSpec.
- Implement product behavior.
- Select intraday/calendar, analytical, or distributed architecture.
- Retrofit M1 history.

## Decisions

### Thin slice

M2 proves one canonical stock and one spot-crypto pair over bounded daily OHLCV ranges. Deterministic fixture adapters precede production-visible adapters. CLI/API share application contracts.

### Authority boundary

The PRD, D-records, approved REQ entries, ADRs, accepted specification, and evidence plan govern. OpenSpec remains a resumable planning/execution view.

### Provider and licensing gate

No provider is selected until official access, terms, quota, timestamp/adjustment semantics, named credentials, fixture rights, and reproducible failure evidence pass review.

### Persistence gate

M1 SQLite metadata does not decide M2 payload storage. A dedicated ADR must preserve ownership, exact semantics, revisions, bounded reads/repair, local operation, migrations, integrity, and replaceability without importing M3 needs.

## Risks and tradeoffs

- More planning delays code but prevents silent financial-data corruption and licensing violations.
- Fixture-first adapters reduce live realism but make CI deterministic; optional live checks supplement rather than replace conformance.
- Daily expected-date policy is intentionally bounded and may report unresolved uncertainty until M3 calendars exist.

## Validation

- requirements/decision/ADR link inspection;
- strict OpenSpec validation;
- Markdown link, registry, schema, and governance validation;
- authority review for product, architecture, security, data, licensing, and quality;
- no implementation task may begin before entry acceptance.
