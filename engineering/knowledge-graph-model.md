# Architecture Knowledge Graph Model

The architecture registry is the machine-readable index; this model defines the governed relationships among artifacts.

## Node types

- Intent
- Requirement
- Quality attribute
- ADR
- Capability
- Contract family and revision
- Workflow
- Extension point
- Specification
- Risk
- Test or fitness rule
- Migration
- Telemetry contract
- Milestone
- Evidence artifact

## Core relationships

```text
Intent derives Requirement
Requirement satisfied_by Specification
Specification constrained_by ADR
Capability owns Contract and State
Capability consumes or produces Contract
Workflow coordinates Capability
Extension implements ExtensionPoint
Implementation implements Specification
Test verifies Requirement, ADR, or Contract
Telemetry observes Capability, Workflow, and Contract
Migration migrates Contract or State
Evidence proves Verification
ADR supersedes ADR
```

## Governance rules

- Every relationship references stable identifiers from the registry.
- Public contracts have exactly one accountable owner.
- Tests and fitness rules identify what they verify rather than merely where they run.
- Superseded artifacts remain queryable for historical impact analysis.
- Generated views never become more authoritative than their source artifacts.
- Sensitive metadata is referenced rather than copied into the graph.

## Initial uses

The graph should support questions such as:

- Which requirements and tests are affected by changing a contract family?
- Which capabilities consume an event revision?
- Which ADRs constrain workflow persistence?
- Which recovery exercises validate a quality attribute?
- Which extensions require a permission or seam being changed?

## Implementation posture

M0.x defines identifiers, relations, and validation rules only. Storage and query technology remain deferred until concrete automation requirements justify a choice.
