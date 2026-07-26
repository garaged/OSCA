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
- **M6 backtesting and strategy validation foundation:** Complete
- **M7 F2 event-driven validation foundation:** Complete
- **M8 F3 paper evaluation and automation foundation:** Complete
- **M9 governed ML lifecycle foundation:** Complete
- **M10 LLM lifecycle and gateway foundation:** Complete
- **M11 analytical breadth and portfolio intelligence:** Complete
- **M12 release readiness and operational resilience:** Complete
- **P1 provider production promotion evidence gates:** Complete
- **P2 no-cost provider discovery baseline:** Complete
- **P3 no-cost provider profile catalog:** Complete
- **P4 no-cost provider adapter contracts:** Complete
- **P5 state reconciliation and operator surface:** Complete
- **Current activity:** P6 no-cost local OHLCV import provider
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

## M7 completion boundary

M7 is complete through its governed exit review and archived OpenSpec change. M7 provides deterministic F2 event-driven validation contracts, order lifecycle evidence, simulated fills, fill model metadata, deterministic risk decisions, balanced journal transactions, valuation snapshots, rebuildable projections, promotion gates, validation services, fill settlement helpers, and SQLite metadata persistence for F2 validation evidence.

F3 forward paper evaluation, independent paper accounts, durable market-aware schedules, runtime strategy execution, ML, LLM, live execution, tick/quote/order-book fidelity, and provider production promotion remain deferred until later governed milestone intents.

## M8 completion boundary

M8 is complete through its governed exit review and archived OpenSpec change. M8 provides F3 paper evaluation contracts, independent paper account identity, approved-candidate linkage from M7 promotion gates, forward paper run requests, data and operational health gates, pause and kill-switch controls, backtest-versus-forward comparison records, durable schedule identity, missed-run policy, checkpoint and recovery decisions, SQLite metadata persistence, notification inbox records, digests, delivery-adapter declarations, and skipped delivery attempts for disabled adapters.

Live execution, broker/exchange adapters, real-capital orders, ML, LLM, F4 fidelity, and provider production promotion remain deferred until later governed milestone intents.

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
- [M8 milestone](docs/milestones/m8/README.md)
- [M9 milestone](docs/milestones/m9/README.md)
- [M10 milestone](docs/milestones/m10/README.md)
- [M11 milestone](docs/milestones/m11/README.md)
- [M12 milestone](docs/milestones/m12/README.md)
- [P1 milestone](docs/milestones/p1/README.md)
- [P2 milestone](docs/milestones/p2/README.md)
- [P3 milestone](docs/milestones/p3/README.md)
- [P4 milestone](docs/milestones/p4/README.md)

## M9 completion boundary

M9 is complete through its governed exit review and archived OpenSpec change. M9 provides governed ML feature and label definitions, training workflow metadata, experiment and model artifact records, evaluation and calibration reports, deterministic promotion decisions, SQLite lifecycle metadata persistence, F2 event-validation links, champion/challenger paper deployment decisions, drift/outcome monitoring reports, and retraining records without automatic promotion.

Trainer execution, production model serving, LLM behavior, live execution, real-capital orders, F4 fidelity, and provider production promotion remain deferred to later governed milestone intents.

## M10 completion boundary

M10 is complete through its governed exit review and archived OpenSpec change. M10 provides governed LLM provider/model capability records, prompt templates, bounded tool definitions, explicit project-context policies, structured-output contracts, request envelopes, deterministic route decisions, privacy and budget gates, evaluation reports, and SQLite lifecycle metadata persistence without invoking providers.

Provider adapters, prompt execution, retrieval materialization, generated recommendations, LLM tool orchestration, state-changing execution, live execution, real-capital orders, and provider production promotion remain deferred to later governed milestone intents.


## M11 completion boundary

M11 is complete through its governed exit review and archived OpenSpec change. M11 provides governed analytical pack manifests, deterministic pack validation, analytical result bundles, method comparison, outcome calibration, portfolio scenario evidence, cross-family synthesis records, visualization pack metadata, and SQLite metadata persistence for analytical breadth and portfolio intelligence.

Runtime fundamental, macro, event, news, sentiment, on-chain, specialized ML, and visualization engines; provider calls; LLM-generated synthesis; recommendation execution; live execution; real-capital orders; and provider production promotion remain deferred to later governed milestone intents.

## M12 completion boundary

M12 is complete through its governed exit review and archived OpenSpec change. M12 provides governed release-readiness and operational-resilience contracts for backup manifests, restore verification, disaster-recovery exercises, health findings, alert policies, workflow run records, deterministic risk-policy decisions, and SQLite metadata persistence.

Real off-device backup transport, active restore execution, external alert delivery, runtime scheduler execution, personal-server transport implementation, live execution, real-capital orders, and provider production promotion remain deferred until later governed milestone intents.


## P1 completion boundary

P1 is complete through its governed exit review and hosted Quality evidence. P1 defines provider production evidence bundles, deterministic promotion decisions, and SQLite metadata persistence for Twelve Data and Kraken provider production promotion evidence.

Real provider calls, credential value access, production ingestion jobs, external redistribution/export implementation, runtime provider scheduling, live execution, and real-capital orders remain deferred until later governed milestone intents.

- P1 clarification: provider promotion now preserves an explicit no-cost provider baseline so OSCA can function without requiring user spend when complete free-tier/no-cost evidence is available.
- No-cost baseline clarification Quality: `30183593760` at `eba603a...`.


## P2 completion boundary

P2 is complete through its governed exit review and hosted Quality evidence. P2 records candidate provider dispositions, official-source notes, no-cost constraints, and exclusion policy without implementing adapters, invoking provider APIs, changing runtime routing, or promoting providers to production.

- P2 Quality: `30184477700` at `0e13f84...`.


## P3 completion boundary

P3 is complete through its governed exit review and hosted Quality evidence. It adds executable no-cost provider profile selection and implementation-readiness classification while keeping provider adapters, provider API calls, credential materialization, runtime routing, production promotion, and external redistribution/export enablement deferred until later governed milestone intents.

- P3 Quality: 30186073205 at 31d0d11....


## P4 completion boundary

P4 is complete through its governed exit review and hosted Quality evidence. It defines fixture-backed adapter contracts for SEC EDGAR and FRED. Live provider calls, credential materialization, runtime routing, production promotion, and production ingestion remain deferred until later governed milestone intents.

- P4 Quality: `30191624710` at `fef440b...`.


## Planned P5-P17 implementation sequence

The remaining P milestone sequence is planned in [Remaining P Milestone Roadmap](docs/milestones/remaining-p-roadmap.md). P5 completed the required M0-M12 and P1-P4 documentation and implementation drift review before the next functional work begins.

- **P5:** State reconciliation and operator surface complete.
- **P6-P7:** Minimum usable local/demo tool through local OHLCV import and first demo research workflow.
- **P8-P12:** Useful analyst workflow through backtest-to-paper, official enrichment preview, routing, workspace, and optional ML/LLM preview.
- **P13-P15:** Production-capable version through promoted provider ingestion, production operations, and runtime extensions.
- **P16-P17:** Real-money readiness only if explicitly approved through a go/no-go study and controlled pilot gates.


## P5 completion boundary

P5 is complete through its governed exit review and merged implementation. It reconciles the M0-M12 and P1-P4 status boundary and exposes provider promotion status, no-cost provider catalog readiness, fixture-backed adapter contracts, and fixture validation through CLI operator commands.

Live provider calls, credential materialization, runtime provider routing, production ingestion, and real-capital orders remain disabled and deferred until later governed milestone intents.
