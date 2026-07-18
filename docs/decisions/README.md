# Architecture Decision Records

- **Status:** Draft
- **Governing role:** Architecture authority
- **Purpose:** Index consequential technical decisions and their lifecycle.
- **Authoritative sources:** PRD sections 38 and 40; active product decisions
- **Downstream consumers:** Architecture, specifications, implementation, reviews, migrations, risks, and documentation

## Scope

An ADR records a consequential technical or engineering-governance choice that:

- constrains multiple components or milestones;
- is expensive or risky to reverse;
- establishes a compatibility, security, data, or operational contract;
- resolves a meaningful tradeoff among viable alternatives; or
- creates an architecture fitness obligation.

ADRs cannot change product scope or weaken an accepted product requirement. Such changes require product decision governance first.

## Lifecycle

ADR statuses are Proposed, Accepted, Superseded, Rejected, and Deprecated.

Accepted ADRs remain authoritative within their declared scope until explicitly superseded. Supersession links both records and includes migration and compatibility consequences.

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-requirements-authority-and-traceability-model.md) | Requirements authority and traceability model | Accepted |
| [ADR-0002](ADR-0002-modular-monolith-decomposition-model.md) | Modular-monolith decomposition model | Accepted |

## Template

Use [adr-template.md](adr-template.md) for new decisions.
