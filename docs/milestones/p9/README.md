# P9 - SEC Preview and FRED Terms Gate

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Add safe opt-in SEC EDGAR enrichment preview while keeping FRED live access policy-blocked until accepted licensing evidence permits OSCA's intended use and retention model.
- **Baseline:** Completed M0-M12 roadmap and P1-P8
- **Last reviewed:** 2026-07-31
- **Validation:** Focused local tests passed; hosted Quality pending on PR #52

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p9-sec-fred-live-preview-adapters.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p9-sec-fred-live-preview-adapters/spec.md)
- [Requirements and traceability reconciliation](../../governance/p8-p9-reconciliation.md)
- [User testing quickstart](user-testing-quickstart.md)
- [Exit review](exit-review.md)

## Objective

Implement an explicit, preview-only SEC EDGAR enrichment path behind fail-closed network, fair-access, cache, and provenance controls. Preserve the FRED adapter contract for fixture-level conformance while blocking live FRED API requests, secret resolution, and content retention under current terms.

## User-visible value

Analysts can replay deterministic SEC fixtures immediately and can explicitly opt into bounded SEC company-facts or submissions previews using an official public source. FRED attempts return structured policy-blocked evidence instead of silently using credentials or retaining data.

## Implementation scope

- Add SEC company-facts and submissions preview requests and evidence contracts.
- Support deterministic fixture replay with network access disabled.
- Require explicit `--enable-network` for SEC live preview.
- Require a declared organization and contact-email user agent.
- Restrict requests to approved `https://data.sec.gov` endpoints.
- Apply conservative throttling at no more than 9 requests per second, with a default of 2 requests per second.
- Apply bounded timeouts and response-size limits.
- Cache SEC preview payloads and retain source URI, checksum, record count, and evidence metadata.
- Expose a focused module CLI through `python -m osca.provider_preview`.
- Reclassify FRED live implementation readiness to `NEEDS_EVIDENCE`.
- Preserve the network-disabled FRED fixture contract while blocking live requests, API-key resolution, caching, and archival.

## Explicit non-scope

- FRED live API calls or FRED content retention.
- OHLCV substitution.
- Runtime provider routing.
- Production provider promotion or production ingestion.
- Paid provider calls.
- Recommendations, broker connections, autonomous execution, or real-capital orders.

## Acceptance criteria

- REQ-0219-REQ-0225 remain allocated to P9 and reflect the corrected SEC-live/FRED-blocked scope.
- SEC fixture replay succeeds without network access.
- SEC live preview requires explicit network enablement and a non-placeholder declared user agent.
- SEC requests fail closed for unapproved hosts/paths, malformed JSON, oversized payloads, and provider errors.
- Repeated SEC requests can resolve from the bounded local cache without another network call.
- FRED live attempts return a policy-blocked result without resolving a named secret reference.
- Automated tests cover positive, cache, validation, credential, and deferred-boundary behavior.
- Manual testing and usage guidance matches the implemented module CLI.
- Hosted Quality passes before P9 is marked complete.

## Validation gates

- Ruff, strict mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, terms-gate, and manual-testing review.
- Exit review recording implemented, fixture-backed, policy-blocked, and deferred behavior.

## Dependencies

P4 fixture-backed adapter contracts, P5 provider governance, P6 local storage conventions, P7 analyst evidence, and completed P8 evidence workflow.

## Terms decision

Current FRED terms prohibit storing, caching, or archiving FRED content and require separate evidence for software/AI-related use. Under D-040, technical accessibility is insufficient permission. P9 therefore does not invoke FRED, resolve its API-key reference, or retain FRED content.

SEC official guidance permits scripted EDGAR access when callers declare a meaningful user agent and respect the current maximum of 10 requests per second. P9 uses a stricter implementation ceiling of 9 requests per second and defaults to 2.

## Residual risks

- Provider terms and access policies can change and must be rechecked before later promotion.
- SEC preview data is enrichment evidence, not an OHLCV substitute or recommendation.
- The module CLI is an isolated preview surface; P10 remains responsible for governed runtime routing.
