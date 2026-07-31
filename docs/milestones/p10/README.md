# P10 - Capability-Based Runtime Provider Routing

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Route supported data capabilities through explicit governed sources while recording selected, stale, policy-blocked, provider-unavailable, and partial outcomes.
- **Baseline:** Completed M0-M12 roadmap and P1-P9
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality pending on PR #53

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p10-runtime-provider-routing.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p10-runtime-provider-routing/spec.md)
- [Requirements and traceability reconciliation](../../governance/p9-p10-reconciliation.md)
- [User testing quickstart](user-testing-quickstart.md)
- [Exit review](exit-review.md)

## Objective

Introduce a single capability-oriented routing surface for governed local OHLCV payloads and SEC enrichment evidence without making OSCA depend on FRED or any paid provider.

## User-visible value

Users can request OHLCV, company facts, filings, or macro enrichment and receive a structured explanation of which source was selected or why the capability is blocked or unavailable. A blocked macro request does not stop supported non-macro work.

## Source precedence

| Capability | Ordered selectable sources | No selectable source |
|---|---|---|
| OHLCV | Explicit governed local Parquet payload | `provider_unavailable` |
| Company facts | Explicit SEC fixture, then explicit opt-in SEC live preview | `provider_unavailable` |
| Filings | Explicit SEC fixture, then explicit opt-in SEC live preview | `provider_unavailable` |
| Macro series | None while FRED remains gated | `policy_blocked` for FRED; `provider_unavailable` for any unconfigured alternative |

P10 never silently blends sources or substitutes one capability for another.

## Implementation scope

- Add immutable routing request, decision, and batch-result contracts.
- Route explicit governed local Parquet OHLCV payloads.
- Route P9 SEC fixture and opt-in live-preview evidence for company facts and filings.
- Record source/provider identity, payload provenance, cache state, network use, stale state, findings, and rationale.
- Fail closed when an available payload is stale unless the caller explicitly allows stale evidence.
- Return `policy_blocked` for FRED macro requests without network use, credential materialization, caching, or payload selection.
- Return `provider_unavailable` when no approved source can satisfy a capability.
- Keep successful non-macro decisions when a mixed batch also contains blocked or unavailable macro requests, reporting the batch as `partial`.
- Expose API and CLI inspection through `python -m osca.runtime_routing`.

## Explicit non-scope

- Automatic discovery or fallback across arbitrary files or providers.
- FRED live API calls, credential resolution, caching, or archival.
- Production promotion of paid/authenticated providers.
- Production ingestion scheduling, real-time streaming, or source blending.
- Recommendations, broker connections, autonomous execution, or real-capital orders.

## Acceptance criteria

- REQ-0226-REQ-0232 reflect the capability-based routing and macro-independence semantics.
- Local OHLCV and SEC fixture routing are demonstrable with network disabled.
- SEC live preview remains explicit and inherits all P9 safety controls.
- Stale evidence is visible and fails closed unless explicitly allowed.
- FRED returns `policy_blocked`; an unknown macro provider returns `provider_unavailable`.
- A mixed macro/non-macro batch retains successful non-macro decisions and reports `partial`.
- CLI policy inspection shows the exact capability matrix.
- Automated tests cover selected, stale, unavailable, blocked, partial, validation, and deferred-boundary behavior.
- Manual usage, traceability, OpenSpec, exit evidence, and hosted Quality are current before completion is marked.

## Validation gates

- Ruff, strict mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, routing-policy, and manual-testing review.
- Exit review recording implemented, fixture-backed, optional-preview, policy-blocked, unavailable, and deferred behavior.

## Dependencies

P6 governed local OHLCV payloads and P9 SEC preview/FRED terms gate.

## Risks and decisions

- Source routing is capability-based; SEC is not treated as a substitute for macro-series data.
- FRED is optional and not a platform dependency.
- Provider failures and stale data remain explicit rather than being hidden through fallback.
- P11 may consume routing decisions but must preserve their status and provenance without silently changing source selection.
