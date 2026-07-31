# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P11 deterministic local analyst path:** Complete
- **P12 optional model-assisted preview:** Complete through PR #55
- **Current activity:** P13 governed production provider admission and ingestion candidate in PR #56
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## P13 admission boundary

P13 adds `osca.production_ingestion` with an auditable provider/resource admission decision before every run.

- **SEC EDGAR:** approved only for company facts and submissions from official `data.sec.gov`, with a declared user agent and internal-use-only retention.
- **Kraken:** approved only for public spot OHLC from official `api.kraken.com`, for personal/internal use.
- **Twelve Data, Alpha Vantage, Nasdaq Data Link:** `needs_evidence` pending exact account-plan, dataset, retention, export, and redistribution rights.
- **FRED:** `policy_blocked` pending retention and software/AI-use evidence.

Approved runs require explicit network opt-in, HTTPS allowlists, bounded timeout/size/retries, valid JSON, and atomic payload/metadata retention with SHA-256 lineage. A policy downgrade blocks future runs without deleting historical evidence.

## Preserved boundaries

P13 does not enable external redistribution, public multi-user data service, paid/authenticated provider promotion without evidence, real-time streaming, recommendations, brokers, autonomous execution, or real-capital orders.

## Authoritative navigation

- [P13 milestone](docs/milestones/p13/README.md)
- [P13 quickstart](docs/milestones/p13/user-testing-quickstart.md)
- [P12-P13 reconciliation](docs/governance/p12-p13-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Validation state

P12 is complete with final Quality run `30646021643` and merge commit `03aca9f71db0087c2ef6df5b176baae219cbf99e`. P13 remains an implementation candidate until PR #56 passes final hosted Quality, review, and evidence reconciliation.
