# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0 architecture foundation:** Merged through PR #2
- **M0.x operationalization:** Complete
- **M1-M12 governed foundation roadmap:** Complete
- **P1-P5 provider governance and reconciliation:** Complete
- **P6 no-cost local OHLCV import:** Complete
- **P7 deterministic demo research workflow:** Complete
- **P8 backtest-to-paper evidence path:** Complete, including macOS Apple Silicon/Python 3.13 manual validation
- **Current activity:** P9 SEC preview and FRED terms gate implementation candidate in PR #52
- **Next practical product path:** P10 governed runtime routing, then P11 analyst workspace
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## Authoritative navigation

- [Product requirements](docs/product-requirements.md)
- [Decision log](docs/decision-log.md)
- [Architecture handbook](docs/handbook/README.md)
- [Architecture decisions](docs/decisions/README.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability register](docs/governance/traceability-register.md)
- [P8-P9 requirements and traceability reconciliation](docs/governance/p8-p9-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Manual testing and usage](docs/testing/manual-testing.md)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Completed foundation boundary

M0-M12 provide the governed modular-monolith foundation, secure local-first operation, canonical data and temporal contracts, research-project and extension contracts, backtesting and event-driven simulation foundations, paper-evaluation/accounting foundations, ML and LLM lifecycle governance, analytical-pack metadata, and operational-resilience contracts.

Many M0-M12 capabilities are contract, metadata, persistence, or validation foundations rather than complete production runtime engines. Their milestone exit records and OpenSpec artifacts remain authoritative for exact implemented versus specified-only scope.

## Provider governance boundary

P1-P5 provide provider promotion evidence gates, a no-cost provider catalog, readiness classification, fixture-backed SEC EDGAR and FRED adapter contracts, and operator-facing provider-governance surfaces.

Technical accessibility is not licensing permission. D-040 requires retrieval, retention, transformation, export, backup, redistribution, credential, quota, and account-plan evidence where applicable. Unknown or conflicting provider rights fail closed.

- SEC EDGAR remains the preferred public no-key enrichment source subject to declared user-agent and fair-access controls.
- FRED remains a preferred official macro candidate at the catalog level, but live implementation readiness is `NEEDS_EVIDENCE` under current terms.
- The FRED fixture contract remains available for deterministic conformance only.
- Twelve Data and Kraken remain production-promotion candidates, not enabled runtime providers.
- Alpha Vantage and Nasdaq Data Link remain conditional.
- Stooq remains research-only.
- Unofficial Yahoo Finance paths remain excluded.

## P6-P8 usable local workflow boundary

P6-P8 provide the first genuinely usable no-cost local evidence workflow:

1. Import user-supplied CSV or Parquet OHLCV into governed local metadata and Parquet payload storage.
2. Generate a deterministic evidence-only research report.
3. Run the transparent built-in `sma-trend-long-only` strategy against the exact imported payload.
4. Compare strategy evidence with buy-and-hold and retain a linked local paper-evaluation record.

P8 manual validation imported `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv` with `row_count: 10`, processed ten AAPL daily bars, generated three simulated evidence trades, and retained paper run `aaad0f77-aebd-455b-832a-9df9feafb680` in `local-evidence-only` mode. See [retained P8 evidence](evidence/p8/manual-backtest-paper-report.md).

This is a local analyst/engineering CLI path. It is not live paper trading, a broker integration, a recommendation engine, a scheduler, or real-capital execution.

## P9 implementation-candidate boundary

P9 adds `osca.provider_preview` as an isolated preview surface:

- Deterministic SEC company-facts fixture replay with network disabled.
- Explicit opt-in SEC company-facts and submissions requests.
- Required organization/contact user agent.
- Approved HTTPS `data.sec.gov` host and path restrictions.
- Conservative fair-access throttling, bounded timeout, and bounded response size.
- Atomic local SEC cache plus source, checksum, record-count, cache-state, and safety-boundary evidence.
- Structured FRED policy-blocked evidence with no API request, no credential resolution, and no content retention.

P9 does not introduce general runtime provider routing. P10 owns one governed resolution surface across local imports, fixtures, approved previews, stale/unavailable states, and policy blocks.

## Practical analyst-product gap

Capabilities usable now:

- Local CSV/Parquet OHLCV import.
- Deterministic research metrics and static reports.
- Transparent historical strategy evidence.
- Buy-and-hold comparison.
- Local paper-evaluation evidence.
- Deterministic SEC fixture enrichment and optional bounded SEC live preview after P9 acceptance.

Major gaps before a practical local analyst product:

- P10: coherent source and enrichment routing with visible provenance and blocked/stale states.
- P11: a workspace for projects, datasets, reports, backtests, and enrichment evidence without manual payload-path handling.
- Executable analytical and visualization depth beyond the current narrow research/backtest path should be explicitly owned by P11 or a later governed milestone.

P12 ML/LLM previews are optional enhancements and are not required for deterministic local usefulness.

## Deferred production and trading boundary

The following remain disabled unless a later milestone explicitly owns them and passes all gates:

- FRED live API access, key resolution, caching, or archival.
- Broad live provider routing or automatic fallback.
- Scheduled production ingestion.
- Provider production promotion without exact accepted evidence.
- Paid-provider use without explicit cost/account-plan approval.
- Generated investment recommendations presented as authoritative facts.
- Broker or exchange connections.
- Autonomous strategy execution.
- Live or real-capital orders.

P13-P15 remain deferred behind licensing, security, operational, packaging, and recovery evidence. P16 is only a go/no-go study for live-order readiness. P17 is not authorized unless P16 explicitly approves it through a separate governed decision.

## Validation state

P8 implementation, compatibility, documentation, and manual-validation evidence is complete. P9 remains an implementation candidate until PR #52 passes hosted Ruff, strict mypy, tests/contracts/migrations/links/architecture, OpenSpec, secret scanning, review, and any required manual smoke validation.
