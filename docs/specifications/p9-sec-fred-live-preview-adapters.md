# P9 SEC Preview and FRED Terms Gate Specification

## Purpose

Implement an opt-in SEC EDGAR enrichment preview behind fail-closed network, fair-access, cache, and provenance controls while keeping FRED live API access policy-blocked until accepted terms evidence permits OSCA's software use and retention model.

## Phase

Useful analyst workflow

## User-visible value

Analysts can replay deterministic SEC fixtures and explicitly retrieve bounded official SEC company-facts or submissions previews. Attempts to use FRED live return structured policy-blocked evidence without credential resolution or content retention.

## Requirements

- REQ-0219-REQ-0225: OSCA must implement the corrected P9 scope described by this specification before P9 is marked complete.
- REQ-0219-REQ-0225: P9 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred or terms-blocked behavior.
- REQ-0219-REQ-0225: P9 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## SEC preview contracts

A SEC preview request must preserve:

- Stable request identity.
- Supported endpoint identity: company facts or submissions.
- Normalized CIK identity.
- Explicit network-access state.
- Optional deterministic fixture path when network access is disabled.
- Declared user-agent when network access is enabled.
- Force-refresh intent, timeout, and maximum response size.

Successful evidence must preserve:

- Provider, endpoint, CIK, execution mode, and outcome.
- Source URI and payload URI.
- Payload SHA-256 and provider-specific record count.
- Cache-hit and network-use state.
- Evidence-only and deferred-boundary flags.
- Generated timestamp and rationale.

## SEC network policy

- Network access is disabled unless the caller explicitly enables it.
- Live preview and fixture replay are mutually exclusive.
- The user agent must identify an organization and contact email and must reject placeholder identity.
- Requests are restricted to HTTPS on `data.sec.gov` and approved company-facts or submissions paths.
- The service defaults to 2 requests per second and must reject configuration above 9 requests per second.
- Requests use bounded timeouts and response-size limits.
- HTTP errors, transport failures, malformed JSON, missing provider structures, and oversized payloads fail closed.

## SEC cache and provenance

- Live SEC responses may be cached only under the caller's configured local storage root.
- Cache paths are provider-, endpoint-, and CIK-scoped.
- Writes are atomic.
- A cache hit avoids another network request unless force refresh is explicitly selected.
- Evidence metadata records the source, payload location, checksum, record count, network state, and safety boundaries.
- Fixture replay reads the supplied fixture directly and does not imply production ingestion.

## FRED terms gate

- The FRED fixture-backed adapter contract remains available for deterministic conformance tests.
- FRED live implementation readiness is `NEEDS_EVIDENCE` while blocking terms constraints remain unresolved.
- P9 must not invoke the FRED API.
- P9 must not resolve or materialize a FRED API-key reference.
- P9 must not store, cache, archive, or incorporate FRED API content into OSCA storage.
- A FRED preview attempt returns structured policy-blocked evidence and no payload.
- Embedded secret values are rejected; only named `secret:` references are syntactically accepted, and they remain unresolved.

## Implementation scope

- `osca.provider_preview` contracts, service, transport boundary, fair-access gate, and module CLI.
- SEC fixture and deterministic replay tests.
- SEC opt-in live preview with cache/provenance behavior.
- FRED policy-blocked decision behavior.
- Provider catalog readiness correction and preserved fixture contract.
- User documentation, OpenSpec, traceability, manual testing, and exit evidence.

## Explicit non-scope

- FRED live API calls or content retention.
- OHLCV substitution.
- Runtime provider routing or fallback.
- Production provider promotion or scheduled ingestion.
- Paid-provider calls.
- Investment recommendations, broker execution, autonomous trading, or real-capital orders.

## Acceptance criteria

- Fixture replay succeeds without network access.
- SEC live preview requires explicit opt-in and a valid declared user agent.
- Approved SEC URLs are constructed deterministically from endpoint and normalized CIK.
- Cache behavior is deterministic and tested without real network calls.
- FRED requests remain blocked without credential resolution or payload retention.
- Existing P4 FRED fixture-contract tests remain valid.
- Provider readiness tests identify the blocking FRED terms constraints.
- Documentation and traceability distinguish implemented SEC preview, fixture-backed contracts, FRED policy block, and deferred production behavior.
- Hosted Quality passes before completion.

## Dependencies

P4 adapter contracts, P5 provider governance, P6 storage conventions, P7 analyst evidence, and completed P8 backtest-to-paper workflow.

## Risks and decisions

D-040 governs the implementation: retrievability is not sufficient licensing evidence. Provider terms and fair-access constraints must be rechecked before any later production promotion or widening of retained content.
