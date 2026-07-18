# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0 architecture foundation:** Merged through PR #2
- **Tier-1 ADRs:** Frozen at M1 implementation entry
- **Architecture review:** Approved
- **M0.x operationalization:** Complete
- **M1 secure walking skeleton:** Accepted
- **Current activity:** M2.0 entry decisions; persistence accepted, provider/licensing selection pending
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

## M1 completion boundary

M1 is accepted through its governed exit review. M1.1–M1.8 provide the secure walking skeleton and retained evidence. Subsequent product work must begin with a new milestone intent, exact requirement allocation, triggered decisions, accepted specification, and proportional evidence plan; M1 acceptance does not authorize implementing later PRD scope early.

## M2 entry state

The M2 initiation package is accepted. [ADR-0017](docs/decisions/ADR-0017-m2-metadata-and-daily-payload-persistence.md) selects capability-owned SQLite metadata and manifest-governed Parquet daily payloads, authorizing M2.1 metadata work. Production-visible provider adapters remain gated by provider-specific licensing and policy approval.

## Key navigation

- [M0.x index](docs/milestones/m0x/README.md)
- [Gap analysis](docs/milestones/m0x/gap-analysis.md)
- [Architecture handbook](docs/handbook/README.md)
- [Validation record](docs/validation/m0x-validation-record.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Engineering bootstrap](engineering/bootstrap/README.md)
- [M0.x roadmap](docs/milestones/m0x-roadmap.md)
