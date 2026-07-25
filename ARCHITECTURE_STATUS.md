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
- **M4 research projects, analytics, and visualization:** Complete
- **M5 independent extension packaging and activation:** Complete
- **Current activity:** M7 F2 event-driven validation foundation
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

## M4 completion boundary

M4 is complete through its governed exit review and archived OpenSpec change. M4 provides governed research-project contracts, hypothesis lifecycle evidence, project timeline and promotion behavior, analysis graph validation and planning, analytical output provenance, evidence-report assembly, declarative visualization specifications, visualization export metadata, and dashboard composition.

ML training, backtesting, paper trading, live execution, and provider production promotion remain deferred to later milestones.

## M5 completion boundary

M5 is complete through its governed exit review and archived OpenSpec change. M5 provides governed extension manifest contracts, fail-closed validation, installation records, explicit activation decisions, permission-renewal checks, disable/uninstall impact previews, SQLite lifecycle persistence, and metadata-only CLI administration.

Runtime loading or execution of third-party extension code, public registry operation, HTTP API/UI administration, strategy/backtesting, ML, LLM, paper trading, live execution, and provider production promotion remain deferred to later milestones.

## M6 completion boundary

M6 is complete through its governed exit review and archived OpenSpec change. M6 provides deterministic backtest contracts, fidelity profiles, execution modes, point-in-time data requirements, pinned assumptions, strategy decisions, simulated order intents, execution plans, result metrics, SQLite lifecycle persistence, and metadata-only CLI administration.

Event matching, fills, portfolio accounting, paper journals, runtime strategy execution, ML, LLM, paper trading, live execution, and provider production promotion remain deferred until their exact contracts and evidence are accepted.

## M7 entry boundary

M7 starts from the accepted M6 backtesting contract boundary. M7 may introduce F2 event-driven bar simulation contracts for order lifecycle, fill modeling, deterministic risk outcomes, balanced accounting journals, valuation, reconciliation, rebuildable projections, and promotion-gate evidence.

Forward paper automation, independent paper accounts, durable market-aware schedules, ML, LLM, live execution, tick/quote/order-book fidelity, and provider production promotion remain deferred until later governed milestone intents.

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
- [M5 milestone](docs/milestones/m5/README.md)
- [M6 milestone](docs/milestones/m6/README.md)
- [M7 milestone](docs/milestones/m7/README.md)
