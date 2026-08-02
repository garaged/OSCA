# U9 Governed No-Cost Historical Data Acquisition

- **Status:** Completion candidate pending hosted validation and manual acceptance
- **Predecessor:** U8 real-world workflow reconciliation
- **Roadmap:** [U9-U14 usable release roadmap](../usable-release-roadmap.md)
- **Provider review:** [U9 provider evidence review](provider-evidence-review.md)
- **Exit review:** [U9 exit review](exit-review.md)

## Intent

Allow a new local OSCA user to acquire sufficient historical equity and cryptocurrency data for the principal research demonstration without a paid account or an external preparation script, while preserving licensing, provenance, canonical identity, quality, revision, and safety controls.

## Governing requirements

U9 implements the selected scope of REQ-0021, REQ-0023 through REQ-0038, REQ-0041, REQ-0042, and the universal evidence-based milestone exit gate.

## Implemented outcome

The primary CLI exposes `osca historical-data fetch` with these governed outcomes:

- Kraken public spot OHLC is admitted for personal/internal use through the bounded P13 production-ingestion path.
- Network access remains explicit and disabled by default.
- Raw provider JSON is retained immutably with SHA-256 lineage.
- Kraken provider errors, malformed payloads, ambiguous pair responses, and low-quality rows fail without creating an accepted canonical revision.
- Kraken rate-limit and service-unavailable responses are classified as retryable provider-unavailable outcomes.
- The final current/not-yet-committed Kraken bar is excluded before canonical acceptance.
- Completed rows pass through the existing OHLCV quality, Parquet, SQLite, and deterministic revision service.
- Successful evidence returns the dataset revision ID, canonical payload, metadata path, row count, parser version, source attribution, and safety boundaries.
- Equivalent completed requests durably reuse retained evidence and canonical revisions; concurrent in-process callers share one provider retrieval.
- Parser-version changes produce a new identifiable revision even when normalized values are otherwise equal.
- The governed CSV import remains the offline and equity fallback and is regression-tested for canonical row equivalence.
- A long-form acquired Kraken revision is exercised through the U8 research pipeline with its human gate and disabled execution boundaries.

## Command surface

```bash
uv run osca historical-data fetch XBTUSD crypto kraken \
  --timeframe 1d \
  --network-access-enabled \
  --storage-root .osca/manual-test
```

A parser migration can be made explicit with:

```bash
uv run osca historical-data fetch XBTUSD crypto kraken \
  --timeframe 1d \
  --parser-version kraken-ohlc-v2 \
  --network-access-enabled \
  --storage-root .osca/manual-test
```

Blocked equity evidence can be inspected with:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/manual-test
```

The equity result remains `provider_unavailable` and directs the operator to governed CSV import.

## Provider decision

Kraken is the only admitted live historical-data source in U9. Twelve Data, Alpha Vantage, Nasdaq Data Link, and other equity candidates remain unavailable until exact display, retention, transformation, export, backup, redistribution, account-plan, and termination evidence passes the provider gate.

This is an intentional fail-closed result, not a missing silent fallback.

## Idempotency and revision behavior

The acquisition identity includes provider, asset class, symbol, timeframe, range cursor, and parser version.

- A completed retained result is reused only when its canonical Parquet and SQLite evidence still exist.
- Concurrent equivalent calls within one process share a keyed lock and one provider retrieval.
- A changed payload digest creates a changed canonical source and revision.
- A changed parser version changes the normalized source evidence and revision identity.
- Failed, blocked, or incomplete evidence is not reused as successful work.

## Security and safety

- Network access is limited to admitted HTTPS endpoints.
- No provider secret is required for Kraken public OHLC.
- Named-secret and secret-exclusion requirements remain authoritative for future providers.
- External redistribution remains disabled.
- Recommendations, automatic model promotion, broker connectivity, exchange orders, autonomous execution, and real-capital orders remain disabled.
- Acquisition output is research evidence, not investment advice.

## Validation coverage

Automated coverage includes:

- command discovery and structured blocked-equity output;
- explicit network opt-in;
- raw payload lineage and canonical persistence;
- exclusion of the uncommitted Kraken bar;
- deterministic revision reuse;
- durable provider-call avoidance;
- concurrent request sharing;
- parser-version revision behavior;
- rate-limit classification and retry guidance;
- malformed and ambiguous payload rejection;
- CSV fallback row equivalence;
- U9-acquired revision handoff into the U8 research pipeline;
- preservation of all recommendation and execution boundaries.

## Manual acceptance still required

Before merge or final U9 closeout, run the clean-profile procedure recorded in the exit review:

1. Acquire a real Kraken daily series.
2. Inspect raw and canonical lineage.
3. Run the U8 research pipeline with explicit human approval.
4. Open the loopback-only workspace and confirm discovery.
5. Exercise one blocked equity request and one unavailable/rate-limited path where practical.
6. Retain the resulting command output, artifact paths, and interpretation.

## Exit criteria

U9 is complete when:

- hosted Ruff, strict mypy, pytest, OpenSpec, link, architecture, and secret checks pass;
- the clean-profile manual acceptance is retained;
- one admitted no-cost cryptocurrency path produces a canonical revision and U8 evidence;
- live equity remains explicitly blocked with current terms evidence and a working CSV fallback;
- failure paths remain actionable and non-corrupting;
- documentation matches the final CLI and evidence contracts;
- all recommendation and execution boundaries remain disabled.
