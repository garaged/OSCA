# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0 architecture foundation:** Merged through PR #2
- **Tier-1 ADRs:** Frozen at M1 implementation entry
- **Architecture review:** Approved
- **M0.x operationalization:** Complete
- **M1 secure walking skeleton:** Accepted
- **M2 governed daily-data vertical slice:** Complete
- **M3 multi-timeframe temporal correctness:** Complete
- **Current activity:** M4 research projects, analytics, and visualization in progress
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

M1 is accepted through its governed exit review. M1.1-M1.8 provide the secure walking skeleton and retained evidence. Subsequent product work must begin with a new milestone intent, exact requirement allocation, triggered decisions, accepted specification, and proportional evidence plan; M1 acceptance does not authorize implementing later PRD scope early.

## M2 completion boundary

M2 is complete through its governed exit review and archived OpenSpec change. M2 provides canonical stock and spot-crypto identity, provider-neutral daily-data contracts, deterministic fixture adapters, governed source/canonical persistence, retrieval and repair jobs, quality findings, inspection, and protected cleanup behavior.

Production promotion for paid, authenticated, or license-sensitive provider use is deferred beyond M2 and remains disabled until exact provider-specific licensing, account-plan, credential, quota, and policy evidence is accepted.

## M3 completion boundary

M3 is complete through its governed exit review and archived OpenSpec change. M3 provides approved interval semantics, UTC completed-bar windows, stock exchange-session and crypto UTC boundary models, calendar-aware gap and repair eligibility classification, deterministic resampling lineage, interval-aware dataset/retrieval/storage identity, governed OHLCV Parquet payloads, and interval-aware non-daily OHLCV publication.

Provider production promotion remains deferred and disabled until exact provider-specific evidence is accepted.

## M4 initiation boundary

M4 starts from the completed M3 data baseline. M4 is authorized to add governed research-project, analytical-output, analysis-graph, and visualization-specification contracts while keeping independent extension packaging, ML training, backtesting, paper trading, and live execution deferred to later milestones.

## Key navigation

- [M0.x index](docs/milestones/m0x/README.md)
- [Gap analysis](docs/milestones/m0x/gap-analysis.md)
- [Architecture handbook](docs/handbook/README.md)
- [Validation record](docs/validation/m0x-validation-record.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Engineering bootstrap](engineering/bootstrap/README.md)
- [M0.x roadmap](docs/milestones/m0x-roadmap.md)
- [M1 milestone](docs/milestones/m1/README.md)
- [M2 milestone](docs/milestones/m2/README.md)
- [M3 milestone](docs/milestones/m3/README.md)
- [M4 milestone](docs/milestones/m4/README.md)
