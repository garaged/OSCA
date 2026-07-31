# P10 Exit Review

- **Milestone:** P10 capability-based runtime provider routing
- **Status:** Implementation candidate, review ready
- **Branch:** `agent/p10-capability-runtime-routing`
- **Pull request:** #53
- **Baseline:** `main` at merge commit `70f9eba856e096299d8afc73d547626dbb0595d6`
- **Hosted Quality:** Run `30640551759` passed on implementation head `e163ae65f7055f67a87c6ad6cb042fa7540ae069`

## Implemented evidence

- Immutable routing request, decision, and batch-result contracts.
- Capability matrix for OHLCV, company facts, filings, and macro series.
- Governed local Parquet OHLCV selection.
- P9 SEC fixture and explicit live-preview composition.
- Explicit stale detection and caller-controlled stale selection.
- `policy_blocked` FRED decisions without network use, credential materialization, caching, archival, or payload selection.
- `provider_unavailable` decisions for missing or unconfigured sources.
- Partial batch evidence that preserves successful non-macro decisions when macro routing is blocked or unavailable.
- API exports and `python -m osca.runtime_routing` policy/routing CLI.

## Fixture-backed behavior

- SEC company-facts fixture replay remains deterministic and network-disabled.
- Local OHLCV tests use temporary governed `.parquet` payload paths; P10 routes the payload rather than re-importing or rewriting it.

## Optional preview behavior

- SEC live preview is selectable only through explicit network enablement and retains all P9 host, path, user-agent, throttling, timeout, response-size, cache, and provenance controls.

## Policy-blocked and unavailable behavior

- FRED macro requests return `policy_blocked`.
- Unconfigured macro providers return `provider_unavailable`.
- SEC requests without a fixture or explicit live enablement return `provider_unavailable`.
- Missing, unsupported, stale-without-opt-in, or provider-mismatched local payloads return `provider_unavailable`.

## Deferred boundaries

The following remain disabled:

- automatic source discovery or silent fallback
- FRED live API access, key resolution, caching, or archival
- paid/authenticated provider promotion
- production ingestion or runtime scheduling
- real-time streaming
- recommendations or financial advice
- broker connections, autonomous execution, or real-capital orders

## Automated validation

The repository suite covers:

- selected local OHLCV
- stale fail-closed and explicit stale use
- SEC fixture selection
- SEC no-source unavailability
- FRED policy block
- unconfigured macro-provider unavailability
- partial mixed batch with non-macro continuation
- source-blending validation rejection
- policy inspection
- structured macro CLI result

## Hosted validation

Quality run `30640551759` passed:

- Ruff
- strict mypy across 182 source files
- 309 tests, including all 10 P10 routing tests, contracts, migrations, links, and architecture checks
- OpenSpec doctor and strict validation
- secret scanning

Run `30640369979` previously found one strict-mypy endpoint-literal narrowing issue. The SEC endpoint type was narrowed without changing runtime behavior, after which the complete Quality suite passed.

## Manual validation

The supported workflow is documented in [P10 user testing quickstart](user-testing-quickstart.md). Manual execution is recommended after merge but is not required to weaken any fail-closed boundary.

## Completion decision

REQ-0226 through REQ-0232 are implemented and evidenced for the approved P10 candidate scope. P10 should be marked complete after PR #53 is reviewed and merged. P11 remains the next planned milestone and must preserve P10 source/status provenance.
