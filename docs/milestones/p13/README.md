# P13 - Governed Production Provider Admission and Ingestion

- **Status:** Complete through PR #56
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Admit only provider/resource scopes with accepted evidence and retain durable ingestion lineage under explicit operator control.
- **Baseline:** Completed M0-M12 roadmap and P1-P12
- **Last reviewed:** 2026-07-31
- **Validation:** Final Quality run `30647766605` passed; merged as `b22d23970be25f6425c4e5bd4d8a8ea51bb38335`

## Approved scope

- **SEC EDGAR:** `company_facts` and `submissions`, official `data.sec.gov`, public no-key, declared user agent, internal use only.
- **Kraken:** public spot `OHLC`, official `api.kraken.com`, public no-key, personal/internal use only.

## Not promoted

- **Twelve Data:** `needs_evidence` for exact account plan, market coverage, retention, display/non-display, export, and redistribution rights.
- **Alpha Vantage:** `needs_evidence` for commercial onboarding and exact market-data rights.
- **Nasdaq Data Link:** `needs_evidence` because rights are dataset/order-form specific.
- **FRED:** `policy_blocked` by unresolved retention and software/AI-use constraints.

## Implemented scope

- Immutable admission, request, and ingestion-evidence contracts.
- Auditable provider/resource admission matrix with evidence review date and terms reference.
- Explicit network opt-in, HTTPS host/path allowlists, SEC user-agent requirement, bounded timeout, size, and retry controls.
- Atomic raw JSON and metadata retention with SHA-256 lineage, attempts, admission state, and network state.
- CLI policy inspection plus SEC company-facts and Kraken OHLC ingestion commands.
- Reversible admission: removing or downgrading a policy decision prevents future network activity without deleting retained evidence.

## Preserved non-scope

Redistribution, external SaaS display, unsupported provider endpoints, credential materialization, paid-plan promotion, real-time streaming, recommendations, brokers, autonomous execution, and real-capital orders remain disabled.

## Completion evidence

- REQ-0247-REQ-0253 map to code and tests.
- 332 tests passed, including all eight P13 tests.
- Ruff, strict mypy, contracts, migrations, document links, architecture checks, OpenSpec, and secret scanning passed.
- Manual usage, provider dispositions, and exit evidence are retained.
