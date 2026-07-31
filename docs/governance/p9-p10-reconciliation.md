# P9-P10 Requirements and Traceability Reconciliation

- **Reviewed:** 2026-07-31
- **Baseline:** P9 merged through PR #52 at `70f9eba856e096299d8afc73d547626dbb0595d6`
- **Candidate:** P10 PR #53
- **Purpose:** Preserve append-only governance history while recording the current implementation state of REQ-0219 through REQ-0232.

## P9 closure

| Requirement | Current state | Evidence |
|---|---|---|
| REQ-0219 | Implemented | P9 SEC fixture and explicit preview request contracts |
| REQ-0220 | Implemented | Declared SEC organization/contact user agent and approved HTTPS paths |
| REQ-0221 | Implemented | Conservative throttling, bounded timeout, and response-size controls |
| REQ-0222 | Implemented | Atomic SEC preview cache and payload/metadata provenance |
| REQ-0223 | Implemented | Deterministic fixture replay and cache tests |
| REQ-0224 | Policy-blocked by accepted correction | FRED network, secret resolution, caching, and archival disabled pending accepted evidence |
| REQ-0225 | Implemented | P9 CLI, manual workflow, OpenSpec, tests, exit evidence, and hosted Quality |

P9 is complete after PR #52 merge. FRED remains optional and is not a dependency for later product functionality.

## P10 allocation and implementation candidate

| Requirement | Intended behavior | Candidate evidence |
|---|---|---|
| REQ-0226 | Route requests by capability rather than requiring a provider | `RuntimeRoutingCapability` and `RuntimeRoutingRequest` |
| REQ-0227 | Select only explicit governed local Parquet payloads for P10 OHLCV | `RuntimeRouter._route_local_ohlcv` and tests |
| REQ-0228 | Select explicit SEC fixture before explicit opt-in live preview; never blend sources | SEC routing dispatch, validation, and tests |
| REQ-0229 | Retain source, provider, payload, cache, network, stale, finding, rationale, and safety evidence | `RuntimeRoutingDecision` |
| REQ-0230 | Fail closed for stale evidence unless explicitly allowed | age checks and stale tests |
| REQ-0231 | Return `policy_blocked` for FRED and `provider_unavailable` for unconfigured macro providers | macro routing and CLI tests |
| REQ-0232 | Preserve successful non-macro work and report `partial` for mixed batches | `route_many`, batch contracts, and tests |

## Traceability links

- Milestone: [P10 README](../milestones/p10/README.md)
- Specification: [P10 specification](../specifications/p10-runtime-provider-routing.md)
- OpenSpec: [P10 OpenSpec](../../openspec/specs/p10-runtime-provider-routing/spec.md)
- Implementation: `src/osca/runtime_routing/`
- Tests: `tests/test_p10_runtime_provider_routing.py`
- Manual workflow: [P10 quickstart](../milestones/p10/user-testing-quickstart.md)
- Exit evidence: [P10 exit review](../milestones/p10/exit-review.md)

## Boundary reconciliation

- FRED is an optional macro candidate, not a required provider.
- SEC supports company facts and filings; it is not represented as a macro-series substitute.
- OHLCV remains available through governed local data independent of macro enrichment.
- A macro policy block cannot change successful non-macro decisions into failures.
- Paid providers, production ingestion, recommendations, brokers, autonomous execution, and real-capital orders remain deferred and fail closed.

This focused record supplements the historical requirements catalog and traceability register without rewriting earlier milestone evidence.
