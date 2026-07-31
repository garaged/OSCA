# P13 - Governed Production Provider Admission and Ingestion

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Admit only provider/resource scopes with accepted evidence and retain durable ingestion lineage under explicit operator control.
- **Baseline:** Completed M0-M12 roadmap and P1-P12
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality pending on PR #56

## Approved candidate scope

- **SEC EDGAR:** `company_facts` and `submissions`, official `data.sec.gov`, public no-key, declared user agent, internal use only.
- **Kraken:** public spot `OHLC`, official `api.kraken.com`, public no-key, personal/internal use only.

## Not promoted

- **Twelve Data:** `needs_evidence` for exact account plan, market coverage, retention, display/non-display, export, and redistribution rights.
- **Alpha Vantage:** `needs_evidence` for commercial onboarding and exact market-data rights.
- **Nasdaq Data Link:** `needs_evidence` because rights are dataset/order-form specific.
- **FRED:** `policy_blocked` by unresolved retention and software/AI-use constraints.

## Implementation scope

- Immutable admission, request, and ingestion-evidence contracts.
- Auditable provider/resource admission matrix with evidence review date and terms reference.
- Explicit network opt-in, HTTPS host/path allowlists, SEC user-agent requirement, bounded timeout, size, and retry controls.
- Atomic raw JSON and metadata retention with SHA-256 lineage, attempts, admission state, and network state.
- CLI policy inspection plus SEC company-facts and Kraken OHLC ingestion commands.
- Reversible admission: removing or downgrading a policy decision prevents future network activity without deleting retained evidence.

## Explicit non-scope

- Redistribution, external SaaS display, unsupported provider endpoints, credential materialization, paid-plan promotion, real-time streaming, recommendations, brokers, autonomous execution, or real-capital orders.

## Acceptance criteria

- REQ-0247-REQ-0253 map to code and tests.
- Non-admitted providers fail before network access.
- Approved scopes require explicit network enablement and exact endpoint allowlists.
- Successful jobs retain payload and metadata atomically with verifiable lineage.
- Retries and response limits are bounded and visible.
- Documentation, OpenSpec, traceability, manual usage, exit evidence, and hosted Quality are current before completion.
