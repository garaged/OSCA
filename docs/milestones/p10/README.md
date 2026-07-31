# P10 - Capability-Based Runtime Provider Routing

- **Status:** Complete
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Route supported data capabilities through explicit governed sources while recording selected, stale, policy-blocked, provider-unavailable, and partial outcomes.
- **Baseline:** Completed M0-M12 roadmap and P1-P9
- **Last reviewed:** 2026-07-31
- **Validation:** Final hosted Quality run `30640728330`; merged through PR #53 at `30375cdfdf45c1f5f522bff7a209416ccac1f93f`

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p10-runtime-provider-routing.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p10-runtime-provider-routing/spec.md)
- [Requirements and traceability reconciliation](../../governance/p9-p10-reconciliation.md)
- [P10-P11 completion reconciliation](../../governance/p10-p11-reconciliation.md)
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

## Implemented scope

- Immutable routing request, decision, and batch-result contracts.
- Explicit governed local Parquet OHLCV routing.
- P9 SEC fixture and opt-in live-preview routing for company facts and filings.
- Source/provider identity, payload provenance, cache state, network use, stale state, findings, and rationale.
- Fail-closed stale behavior unless explicitly allowed.
- Structured FRED `policy_blocked` decisions without network or credential use.
- Structured `provider_unavailable` decisions when no approved source can satisfy a capability.
- Partial mixed-batch behavior preserving successful non-macro decisions.
- API and CLI inspection through `python -m osca.runtime_routing`.

## Completion evidence

- Ruff and strict mypy passed.
- 309 tests passed, including all ten P10 routing tests.
- Contracts, migrations, links, architecture, OpenSpec, and secret scanning passed.
- Final review-ready head passed Quality run `30640728330`.
- PR #53 merged as `30375cdfdf45c1f5f522bff7a209416ccac1f93f`.

## Deferred boundaries

P10 does not enable automatic source discovery, silent fallback, FRED live use, paid/authenticated provider promotion, production ingestion, streaming, recommendations, brokers, autonomous execution, or real-capital orders.

## Successor boundary

P11 may consume and display P10 routing decisions but must preserve their source, status, rationale, and provenance without silently changing source selection.
