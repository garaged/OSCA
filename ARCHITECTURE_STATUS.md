# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P5 provider governance and reconciliation:** Complete
- **P6-P8 usable no-cost local evidence workflow:** Complete
- **P9 SEC preview and FRED terms gate:** Complete through PR #52
- **P10 capability-based runtime routing:** Complete through PR #53
- **Current activity:** P11 read-only analyst workspace implementation candidate in PR #54
- **Next optional path:** P12 local ML/LLM previews after P11
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## Authoritative navigation

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Architecture decisions](docs/decisions/README.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability register](docs/governance/traceability-register.md)
- [P10-P11 reconciliation](docs/governance/p10-p11-reconciliation.md)
- [P11 milestone](docs/milestones/p11/README.md)
- [P11 user testing quickstart](docs/milestones/p11/user-testing-quickstart.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Manual testing and usage](docs/testing/manual-testing.md)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Foundation and provider boundary

M0-M12 provide the governed modular-monolith foundation and lifecycle contracts. P1-P5 provide provider governance, evidence gates, catalog/readiness classification, fixture contracts, and operator visibility.

Technical accessibility is not licensing permission. D-040 requires exact provider-specific evidence. SEC EDGAR is approved only for bounded preview behavior. FRED remains optional and policy-blocked. Paid/authenticated providers remain disabled until separate evidence is accepted.

## Usable local analyst path

P6-P10 provide:

1. governed user-supplied CSV/Parquet OHLCV import
2. deterministic evidence-only research reports
3. transparent historical backtest and linked local paper-evaluation evidence
4. deterministic SEC fixture replay and optional bounded SEC preview
5. capability-based routing with selected, stale, unavailable, policy-blocked, and partial outcomes

FRED is not a platform dependency. A blocked macro request does not stop local OHLCV, research, backtesting, SEC enrichment, or other non-macro work.

## P11 workspace boundary

P11 adds `osca.analyst_workspace` as a read-only local inspection surface:

- immutable snapshot, section, item, and status contracts
- P6 SQLite dataset discovery
- retained P7 research and P8 backtest/paper report discovery
- P9 SEC evidence and P10 routing-decision discovery
- honest empty states for optional project/watchlist summaries
- browser page, health endpoint, full snapshot API, and per-section API
- JSON snapshot CLI and loopback-only server binding
- credential-like metadata-key filtering

P11 does not create, edit, delete, import, run analysis, call providers, resolve credentials, produce advice, connect brokers, or place orders.

## Deferred boundary

The following remain disabled:

- FRED live API access, key resolution, caching, or archival
- automatic provider discovery or silent fallback
- paid/authenticated provider promotion without accepted evidence
- scheduled production ingestion or real-time streaming
- remote/public multi-user workspace hosting
- recommendations presented as authoritative advice
- broker or exchange connections
- autonomous strategy execution
- live or real-capital orders

## Validation state

P10 is complete with final Quality run `30640728330` and merge commit `30375cdfdf45c1f5f522bff7a209416ccac1f93f`. P11 remains an implementation candidate until PR #54 passes hosted Ruff, strict mypy, tests/contracts/migrations/links/architecture, OpenSpec, secret scanning, review, and final evidence reconciliation.
