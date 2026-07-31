# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P5 provider governance and reconciliation:** Complete
- **P6-P8 usable no-cost local evidence workflow:** Complete
- **P9 SEC preview and FRED terms gate:** Complete through PR #52
- **Current activity:** P10 capability-based runtime provider routing implementation candidate in PR #53
- **Next practical product path:** P11 analyst workspace
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## Authoritative navigation

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Architecture handbook](docs/handbook/README.md)
- [Architecture decisions](docs/decisions/README.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability register](docs/governance/traceability-register.md)
- [P8-P9 reconciliation](docs/governance/p8-p9-reconciliation.md)
- [P9-P10 reconciliation](docs/governance/p9-p10-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Manual testing and usage](docs/testing/manual-testing.md)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Foundation boundary

M0-M12 provide the governed modular-monolith foundation, secure local-first operation, canonical data and temporal contracts, research-project and extension contracts, backtesting and event-driven simulation foundations, paper-evaluation/accounting foundations, ML and LLM lifecycle governance, analytical-pack metadata, and operational-resilience contracts.

Many foundation capabilities are contracts, metadata, persistence, or validation components rather than complete production runtime engines. Milestone exit records and OpenSpec artifacts remain authoritative for exact implemented versus specified-only scope.

## Provider governance boundary

Technical accessibility is not licensing permission. D-040 requires provider-specific retrieval, retention, transformation, export, backup, redistribution, credential, quota, and account-plan evidence where applicable. Unknown or conflicting rights fail closed.

- SEC EDGAR is an approved public no-key enrichment preview subject to declared user-agent and fair-access controls.
- FRED is an optional macro candidate with live readiness `NEEDS_EVIDENCE`; requests remain policy-blocked.
- The FRED fixture contract exists only for deterministic conformance.
- Twelve Data and Kraken remain production-promotion candidates, not enabled runtime providers.
- Other catalog dispositions remain governed by P1-P5 evidence.

## Usable local analyst boundary

P6-P9 provide:

1. governed user-supplied CSV/Parquet OHLCV import
2. deterministic evidence-only research reports
3. a transparent built-in strategy and historical backtest evidence
4. linked local paper-evaluation evidence
5. deterministic SEC fixture replay
6. optional explicit SEC company-facts/submissions live preview

These are analyst and engineering evidence workflows. They are not investment recommendations, live paper brokers, schedulers, autonomous strategies, or real-capital execution.

## P10 routing boundary

P10 adds `osca.runtime_routing` as one capability-oriented decision surface:

- **OHLCV:** select an explicitly supplied governed local Parquet payload.
- **Company facts:** select an explicit SEC fixture before explicit opt-in SEC live preview.
- **Filings:** select an explicit SEC fixture before explicit opt-in SEC live preview.
- **Macro series:** return `policy_blocked` for FRED or `provider_unavailable` for an unconfigured alternative.

Every decision records source/provider identity, payload provenance, cache state, network use, stale state, findings, rationale, and disabled safety boundaries. Stale evidence fails closed unless explicitly allowed. Routing never silently discovers, blends, or substitutes sources.

Batch routing preserves successful non-macro decisions when macro enrichment is blocked or unavailable and reports the aggregate result as `partial`. Therefore FRED is not a platform dependency.

## Practical analyst-product gap

P11 remains the primary gap before an approachable local analyst product. It should present projects, datasets, routing decisions, reports, backtests, paper evidence, and SEC enrichment without requiring manual payload-path handling while preserving P10 status and provenance.

P12 model-assisted previews are optional. P13-P15 remain evidence-gated production work. P16 is only a go/no-go study for real-money readiness, and P17 is not authorized.

## Deferred boundary

The following remain disabled:

- FRED live API access, key resolution, caching, or archival
- automatic provider discovery or fallback
- paid/authenticated provider promotion without accepted evidence
- scheduled production ingestion or real-time streaming
- recommendations presented as authoritative advice
- broker or exchange connections
- autonomous strategy execution
- live or real-capital orders

## Validation state

P9 is complete with final hosted Quality run `30637941143`. P10 remains an implementation candidate until PR #53 passes hosted Ruff, strict mypy, tests/contracts/migrations/links/architecture, OpenSpec, secret scanning, review, and final evidence reconciliation.
