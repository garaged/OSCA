# ADR-0001 — Requirements Authority and Traceability Model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision owners:** Product authority, architecture authority, and quality authority
- **Scope:** All governed OSCA requirements, milestone specifications, tests, documentation, risks, and implementation evidence
- **Related requirements:** To be assigned during requirements-catalog population
- **Related product decisions:** D-022, D-042, D-045, D-046, D-047
- **Supersedes:** None
- **Superseded by:** None

## Context

The approved PRD and D-001 through D-047 are authoritative, but individual normative statements do not yet have stable identifiers granular enough to support requirement-to-specification-to-test-to-documentation traceability.

Editing identifiers directly into the approved PRD would create a broad baseline change and couple engineering metadata to product prose. Referring only to PRD section numbers and decision IDs would be too coarse for objective acceptance criteria, automated coverage checks, and change-impact analysis.

## Decision drivers

- Preserve the approved product baseline and its readability.
- Assign stable identities to atomic, testable obligations.
- Prevent engineering decomposition from silently changing product meaning.
- Support forward, backward, and change-impact traceability.
- Enable automated quality gates and orphan detection.
- Preserve supersession history and compatibility analysis.

## Considered alternatives

### Alternative A — Add requirement IDs directly to the PRD

**Benefits**

- Requirements and identifiers remain in one document.
- Direct source links are simple.

**Costs and risks**

- Requires a large edit to the approved baseline.
- Mixes product prose with engineering-control metadata.
- Reorganization can destabilize identifiers or readability.

### Alternative B — Preserve the PRD and create a governed requirements catalog

**Benefits**

- Preserves the approved baseline as semantic authority.
- Supports stable identifiers and rich engineering metadata.
- Separates product authority from engineering decomposition.
- Supports automated coverage and impact analysis.

**Costs and risks**

- Creates a second governed artifact requiring drift controls.
- Extraction and decomposition require careful review.

### Alternative C — Use only PRD sections and decision IDs

**Benefits**

- Requires minimal initial work.
- Avoids duplicated statements.

**Costs and risks**

- References are too coarse for atomic verification.
- Weakens automated traceability and impact analysis.
- Makes duplicate and orphan detection unreliable.

## Decision

OSCA will preserve the approved PRD and active accepted decisions as semantic authority and maintain a separately governed requirements catalog.

The catalog assigns immutable `REQ-NNNN` identifiers to atomic, testable requirements derived without semantic change from authoritative sources. Domain, module, and milestone allocation remain metadata rather than parts of the identifier.

The traceability register and automated quality gates will connect catalog requirements to milestone intents, specifications, acceptance criteria, verification evidence, documentation, ADRs, and risks.

## Rationale

Alternative B provides the required granularity and automation capability while minimizing changes to the approved product baseline. It also permits engineering decomposition to evolve without changing product authority, provided each derived requirement remains reviewably linked to its exact source.

## Consequences

### Positive

- The PRD remains readable and authoritative.
- Requirements gain stable identities independent of repository organization.
- Traceability can be validated automatically.
- Supersession and impact analysis become explicit.

### Negative and tradeoffs

- Catalog drift is possible unless checked.
- Requirement extraction adds review work.
- Duplicate normative text must be managed carefully.

### Required follow-up

- Populate the requirements catalog after glossary terminology is sufficiently stable.
- Define machine-readable metadata and validation rules before implementation begins.
- Add traceability checks to the CI quality-gate design.
- Review catalog extraction against the PRD and decision log before approval.

## Fitness and verification

The decision is effective when:

- every active catalog requirement cites exact authoritative sources;
- no catalog statement changes source meaning;
- milestone specifications and tests can reference stable requirement IDs;
- automated checks detect orphaned or stale relationships; and
- superseded authority produces an explicit downstream impact report.

## Migration and compatibility

No product or runtime migration is required. Future tooling may change the physical catalog format, but identifiers and traceability history must remain stable.

## Risks

- Requirement decomposition may accidentally reinterpret an accepted requirement.
- Manual links may drift before automated validation exists.
- Overly broad requirements may remain difficult to verify.

Treatments include governing-role review, exact source citations, decomposition rules, automated orphan checks, and immutable identifiers.

## Revisit triggers

Reconsider this ADR if the catalog cannot be validated reliably, if the PRD adopts a native stable requirement schema, or if repository scale makes the selected catalog representation impractical.
