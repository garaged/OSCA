# P12-P13 Requirements and Traceability Reconciliation

## Baseline

- P12 completed through PR #55 at merge commit `03aca9f71db0087c2ef6df5b176baae219cbf99e`.
- P13 begins from that merged baseline.

## P13 requirements

| Requirement | Outcome | Implementation | Verification |
|---|---|---|---|
| REQ-0247 | Provider admission decisions are explicit and auditable. | `production_ingestion/contracts.py`, `policy.py` | `test_admission_matrix_approves_only_sec_and_kraken` |
| REQ-0248 | Non-admitted providers fail before network activity. | `run_production_ingestion` admission gate | `test_non_admitted_provider_fails_closed` |
| REQ-0249 | Network use is explicit and endpoints are allowlisted. | request contract and endpoint validation | network/host tests |
| REQ-0250 | Approved jobs use bounded timeout, response size, and retries. | production ingestion request/service | retry and size-limit tests |
| REQ-0251 | Successful jobs retain atomic payload and lineage metadata. | `_retain_success` | retention test |
| REQ-0252 | Admission is reversible without deleting historical evidence. | policy-driven admission before each run | policy and fail-closed tests |
| REQ-0253 | Redistribution, unsupported providers, credentials, advice, brokers, and real orders remain disabled. | admission findings, no credential path, milestone boundaries | policy and negative-path tests |

## Provider dispositions

- SEC EDGAR: bounded internal-use admission for company facts and submissions.
- Kraken: bounded personal/internal admission for public spot OHLC.
- Twelve Data, Alpha Vantage, Nasdaq Data Link: `needs_evidence`.
- FRED: `policy_blocked`.

No disposition authorizes external redistribution or a broader provider/resource scope.
