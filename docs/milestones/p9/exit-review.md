# P9 Exit Review

- **Status:** Implementation candidate
- **Scope reviewed:** P8 closeout, SEC fixture replay, opt-in SEC live preview, cache/provenance, fair-access controls, FRED terms gate, provider readiness, module CLI, tests, documentation, OpenSpec, and deferred boundaries
- **Decision:** Pending hosted Quality and PR review
- **Review branch:** `agent/p9-sec-preview-fred-terms-gate`
- **Pull request:** #52

## P8 closeout evidence

P8 is marked complete with:

- Retained macOS Apple Silicon/Python 3.13 manual evidence.
- Correct ten-row AAPL fixture workflow.
- PR #44 implementation evidence.
- Successful compatibility and documentation follow-ups #45-#51.
- Verified REQ-0212-REQ-0218 scope and explicit local-evidence-only boundaries.

## Implemented P9 evidence

P9 adds:

- `src/osca/provider_preview/contracts.py`
- `src/osca/provider_preview/services.py`
- `src/osca/provider_preview/cli.py`
- `src/osca/provider_preview/__main__.py`
- `tests/fixtures/provider_preview/sec_companyfacts_aapl.json`
- `tests/test_p9_sec_preview_fred_terms_gate.py`

The implementation provides deterministic SEC fixture replay and an optional SEC live-preview path with:

- Explicit network opt-in.
- Declared organization/contact user agent.
- Approved HTTPS host/path construction.
- Conservative fair-access throttling.
- Bounded timeout and response size.
- Atomic local SEC cache writes.
- Payload checksum, record count, source URI, cache state, and safety-boundary evidence.

## FRED disposition

FRED remains a preferred official macro source at the catalog level, but live implementation readiness is now `NEEDS_EVIDENCE` because current terms:

- Prohibit storing, caching, or archiving FRED content.
- Require separate legal evidence for OSCA's software/AI-related use.

The existing network-disabled fixture contract remains available for deterministic P4 conformance. P9 does not invoke FRED, resolve an API key, or retain FRED content. Attempts return structured policy-blocked evidence.

## Local focused validation

The isolated P9 implementation was exercised under Python 3.13 before publication:

- 7 focused tests passed.
- Python compilation passed.
- Covered fixture replay, network opt-in validation, non-placeholder user-agent enforcement, bounded cache reuse, fair-access ceiling, FRED policy blocking, secret-value rejection, and module CLI behavior.

Full repository Ruff and strict-mypy execution was unavailable in the connector-only workspace because package-registry access for those tools was unavailable. Hosted Quality is authoritative for repository-wide validation.

## Required hosted gates

- Ruff.
- Strict mypy.
- Pytest, contracts, migrations, links, and architecture validation.
- OpenSpec strict validation.
- Secret scanning.

## Deferred boundaries

P9 does not implement:

- FRED live API calls, key resolution, or content retention.
- OHLCV substitution.
- Runtime provider routing or fallback.
- Production provider promotion or scheduled ingestion.
- Paid provider calls.
- Recommendations, broker connections, autonomous execution, or real-capital orders.

## Completion condition

P9 may be marked complete only after PR #52 review, hosted Quality success, final evidence reconciliation, and any required manual smoke validation.
