# P10 Runtime Provider Routing Specification

## Purpose

Introduce governed capability-based runtime routing across explicit local payloads and approved enrichment previews, with selected, stale, policy-blocked, provider-unavailable, and partial outcomes.

## Phase

Useful analyst workflow

## User-visible value

Users can request supported data capabilities through one product surface and understand which source was selected, why no source was available, or why a source remains policy-blocked. A blocked macro request does not disable supported OHLCV or SEC enrichment workflows.

## Requirements

- **REQ-0226:** OSCA shall represent runtime routing requests by capability rather than requiring a specific provider.
- **REQ-0227:** OHLCV routing shall select only an explicitly supplied governed local Parquet payload in P10.
- **REQ-0228:** Company-facts and filings routing shall select an explicit SEC fixture before an explicit opt-in SEC live preview and shall not silently blend sources.
- **REQ-0229:** Routing decisions shall retain source/provider identity, payload provenance, cache state, network use, stale state, findings, rationale, and deferred safety boundaries.
- **REQ-0230:** Stale evidence shall fail closed unless the caller explicitly allows stale selection.
- **REQ-0231:** FRED macro requests shall return `policy_blocked`; requests for an unconfigured macro provider shall return `provider_unavailable`; neither outcome may resolve credentials, use the network, cache content, or expose a payload.
- **REQ-0232:** Mixed batches shall retain successful non-macro decisions when macro routing is blocked or unavailable and shall report a `partial` outcome.

## Source precedence

1. **OHLCV:** explicitly supplied governed local Parquet payload.
2. **Company facts:** explicit SEC fixture; otherwise explicit opt-in SEC live preview.
3. **Filings:** explicit SEC fixture; otherwise explicit opt-in SEC live preview.
4. **Macro series:** no selectable runtime source while FRED remains gated.

Routing does not infer files, discover arbitrary providers, substitute SEC for macro data, or silently fall through to an unapproved source.

## Routing statuses

- `selected`: one governed source and payload were selected.
- `policy_blocked`: the requested source is known but its use is prohibited by the current policy/evidence gate.
- `provider_unavailable`: no enabled source can satisfy the capability.

Batch outcomes are `succeeded`, `partial`, `blocked`, or `unavailable`. `partial` means at least one request succeeded and at least one request was blocked or unavailable.

## Implementation scope

- Immutable request, decision, and batch-result contracts.
- Local Parquet existence, format, and optional age checks.
- P9 SEC preview composition without weakening its explicit network/user-agent/rate/size/cache controls.
- FRED policy-block composition without resolving a named secret reference.
- Provider/source mismatch detection.
- API methods for one or many requests.
- CLI commands for policy inspection, local OHLCV, SEC company facts, SEC filings, and macro series.

## Explicit non-scope

- Automatic source discovery or implicit fallback.
- FRED live API calls, credential resolution, caching, or archival.
- Paid/authenticated provider promotion or production ingestion.
- Real-time streaming, recommendation generation, brokers, autonomous execution, or real-capital orders.

## Acceptance criteria

- Local OHLCV and SEC fixture decisions are selectable with network disabled.
- SEC requests without a fixture or explicit live-preview enablement return `provider_unavailable`.
- Stale evidence is visible and requires explicit opt-in.
- FRED returns `policy_blocked` and unknown macro providers return `provider_unavailable`.
- A mixed local-OHLCV/FRED batch reports `partial` and `non_macro_continued: true`.
- Policy inspection exposes the exact capability matrix.
- Automated tests cover positive, stale, blocked, unavailable, partial, validation, and deferred-boundary cases.
- Manual testing, requirements, traceability, OpenSpec, exit review, and hosted Quality evidence are current before P10 is marked complete.

## Dependencies

P6 governed local OHLCV payloads and P9 SEC preview/FRED terms gate.

## Risks and decisions

- FRED is optional; OSCA functionality must not require it.
- SEC enrichment is not equivalent to macro-series data and is not used as a substitute.
- Routing failures remain explicit to prevent hidden source blending or legal-policy bypass.
- P11 consumers must display and preserve routing status and provenance.
