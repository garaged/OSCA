# ADR-0020 — M2 Bounded Daily Expected-Date Policy

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, architecture, and data authorities
- **Scope:** M2 daily freshness, gap detection, targeted repair, quality findings, and resolution status
- **Related requirements:** REQ-0034–REQ-0038
- **Related product decisions:** D-018
- **Supersedes:** None
- **Superseded by:** None

## Context

M2 must detect missing daily observations without claiming M3's complete exchange-calendar, session, holiday, corporate-action, or provisional-bar behavior. Provider-reported dates alone cannot reveal omissions, while treating every weekday as a definite stock session would fabricate gaps on holidays and exceptional closures.

## Decision

M2 uses a conservative asset-class reference policy.

For spot-cryptocurrency pairs, every completed UTC calendar date in the requested range is expected. The current UTC date is incomplete until its interval end and is not declared missing.

For stocks, Monday through Friday dates are expected-date candidates, not proof of an exchange session. A candidate becomes:

- observed, when a valid complete daily observation exists;
- missing, only when accepted evidence establishes that the date was an applicable completed session and no valid observation exists;
- unresolved, when holiday, exceptional closure, listing lifecycle, venue/session, provider completeness, or other calendar uncertainty remains.

Saturday and Sunday are not expected stock dates under M2. The policy does not model exchange-specific holidays or sessions.

Unresolved dates produce visible quality/resolution findings. They do not fabricate observations, declare strict completeness, or initiate automatic repair. A targeted repair may include an unresolved date only when an explicit operator request or later evidence establishes an applicable session.

## Consequences

Crypto gap detection is deterministic in UTC. Stock gap detection remains conservative and may report unresolved dates that M3 will later classify precisely. M2 avoids false data and premature calendar dependencies at the cost of incomplete automated stock repair.

Interfaces expose observed, missing, non-expected, incomplete, and unresolved classifications consistently. Provider responses cannot silently redefine expected-date policy.

## Fitness and verification

- crypto properties classify every completed UTC date and exclude the current incomplete date;
- stock properties classify weekends as non-expected and weekdays as candidates;
- uncertain stock candidates produce unresolved findings, never fabricated gaps or bars;
- confirmed stock sessions without observations become targeted missing ranges;
- repair operates only on confirmed missing ranges unless explicitly authorized;
- time-zone and boundary tests cover UTC interval completion;
- no exchange-calendar dependency or M3 session model enters M2.

## Revisit triggers

M3 calendar/session scope begins, M2 evidence shows unacceptable unresolved volume, a supported venue provides authoritative license-safe session evidence, or product requirements demand exchange-specific completeness earlier.
