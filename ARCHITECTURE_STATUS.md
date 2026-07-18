# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0 architecture foundation:** Merged through PR #2
- **Tier-1 ADRs:** Frozen at M1 implementation entry
- **Architecture review:** Approved
- **M0.x operationalization:** Complete
- **Current activity:** M1 secure walking-skeleton implementation
- **Freeze point:** Reached; changes require superseding ADRs

## Governing baseline

ADR-0001 through ADR-0010 are authoritative and have passed the [M0.6 validation program](docs/validation/m0x-validation-record.md). They remain governed by the [architecture evolution policy](engineering/architecture-evolution-policy.md).

M0.x does not redesign M0. It supplies application guidance, validation evidence, lifecycle/exception mechanics, and repeatable M1 initiation controls.

## M0.x completion evidence

- [x] Repository-backed gap analysis
- [x] Non-duplicative architecture handbook
- [x] Technology-neutral reference capability
- [x] Repeatable validation procedure and check manifest
- [x] Validation record and findings disposition
- [x] Harmonized lifecycle and expanded architecture registry
- [x] Architecture exception register
- [x] M1 initiation and review controls
- [x] Evidence record template
- [x] Executable-architecture backlog
- [x] Corrected navigation and stale baseline references

## M1 entry boundary

M0.x is ready for review. Before product implementation begins, M1 planning must select the first vertical slice, assign its exact `REQ-NNNN` requirements, resolve any deferred decisions triggered by that slice, approve its specification, and complete the [M1 initiation checklist](engineering/bootstrap/m1-initiation-checklist.md). These are deliberate M1 entry activities, not incomplete M0 architecture.

## Key navigation

- [M0.x index](docs/milestones/m0x/README.md)
- [Gap analysis](docs/milestones/m0x/gap-analysis.md)
- [Architecture handbook](docs/handbook/README.md)
- [Validation record](docs/validation/m0x-validation-record.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Engineering bootstrap](engineering/bootstrap/README.md)
- [M0.x roadmap](docs/milestones/m0x-roadmap.md)
