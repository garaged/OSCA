# P13 Governed Production Provider Admission and Ingestion Specification

## Purpose

Admit only provider/resource scopes with accepted evidence and implement durable internal-use ingestion with explicit operator control and retained lineage.

## Phase

Production-capable version

## User-visible value

OSCA can retrieve and retain approved SEC and Kraken public data without fixtures or manual imports while explaining why every other candidate remains unavailable or blocked.

## Requirements

- REQ-0247: Provider admission decisions must be explicit, auditable, resource-scoped, and evidence-dated.
- REQ-0248: Non-admitted providers must fail before transport or credential activity.
- REQ-0249: Production network use must be explicit and endpoints must be HTTPS allowlisted.
- REQ-0250: Provider requests must use bounded timeout, response-size, and retry controls.
- REQ-0251: Successful jobs must atomically retain payload and metadata with SHA-256 lineage.
- REQ-0252: Admission must be reversible for future runs without deleting historical evidence.
- REQ-0253: Redistribution, unsupported providers, credentials outside named references, advice, brokers, autonomous execution, and real-capital orders remain disabled.

## Approved scope

- SEC EDGAR company facts and submissions through official `data.sec.gov` endpoints with a declared organization/contact user agent.
- Kraken public spot OHLC through the official public REST endpoint for personal/internal use.

## Evidence-gated or blocked scope

- Twelve Data: exact account-plan and dataset rights required.
- Alpha Vantage: commercial onboarding and exact market-data rights required.
- Nasdaq Data Link: dataset and order-form rights required.
- FRED: policy-blocked pending retention and software/AI-use evidence.

## Implementation scope

- Immutable admission, request, and ingestion evidence contracts.
- Network-free admission-policy inspection.
- Explicit network opt-in, HTTPS host/path allowlists, SEC user-agent enforcement, bounded retries, timeout, and response size.
- Atomic raw JSON and metadata retention with digest, attempts, network state, and admission status.
- CLI commands for policy inspection, SEC company facts, and Kraken OHLC.

## Explicit non-scope

External redistribution, public SaaS display, unsupported endpoints, paid/authenticated provider promotion, real-time streaming, recommendations, broker connections, autonomous execution, and real-capital orders.

## Acceptance criteria

The P13 quickstart and tests demonstrate policy inspection, network fail-closed behavior, non-admitted-provider rejection, endpoint allowlists, successful retained lineage, bounded retries, and response-size enforcement. Hosted Quality and governance reconciliation must pass before completion.
