# Architecture Exception Register

- **Status:** Active
- **Governing role:** Architecture authority
- **Approval roles:** Authority governing the affected rule; security and quality authorities where applicable
- **Purpose:** Record narrow, risk-assessed, expiring deviations without silently changing the architecture baseline.
- **Authoritative sources:** ADR-0005; architecture evolution policy; document control
- **Review frequency:** At every pull request affecting an exception and at least monthly while any exception is active
- **Last reviewed:** 2026-07-18

## Required exception record

Every exception must state:

- stable `EXC-NNNN` identifier and status;
- governing rule and affected artifacts;
- bounded scope and necessity;
- alternatives considered;
- risk, security, compatibility, observability, and recovery impact;
- owner and approving authority;
- creation date, expiry date, and removal trigger;
- compensating controls;
- detection or fitness check where practical;
- remediation plan and closure evidence.

An exception cannot waive product authority, conceal an architecture change, or remain open without an expiry/removal trigger. Consequential permanent change requires a superseding ADR.

## Active exceptions

None.

## Closed exceptions

None.
