# U9 Governed No-Cost Historical Data Acquisition

- **Status:** Implementation candidate, canonical acquisition slice
- **Predecessor:** U8 real-world workflow reconciliation
- **Roadmap:** [U9-U14 usable release roadmap](../usable-release-roadmap.md)
- **Provider review:** [U9 provider evidence review](provider-evidence-review.md)

## Intent

Allow a new local OSCA user to acquire sufficient historical equity and cryptocurrency data for the principal research demonstration without a paid account or an external preparation script, while preserving licensing, provenance, canonical identity, quality, revision, and safety controls.

## Governing requirements

- REQ-0021 canonical instrument identity
- REQ-0023 explicit provider mapping
- REQ-0024 ambiguity protection
- REQ-0025 provider capability contract
- REQ-0026 capability routing
- REQ-0027 visible provider transitions
- REQ-0028 licensing enforcement
- REQ-0029 named provider credentials
- REQ-0030 versioned daily bar contract
- REQ-0031 source immutability and retention evidence
- REQ-0032 canonical revisioning
- REQ-0033 typed dataset metadata
- REQ-0034 explicit retrieval requirements
- REQ-0035 structured resolution status
- REQ-0036 idempotent durable retrieval
- REQ-0037 gap detection and targeted repair
- REQ-0038 initial quality rules
- REQ-0041 approved interval set
- REQ-0042 UTC interval windows
- Universal evidence-based milestone exit gate

## Implemented slices

### Governed acquisition foundation

- Adds the primary `osca historical-data fetch` surface and versioned request/evidence contracts.
- Reuses the admitted P13 Kraken endpoint and resource policy.
- Keeps network use explicit and disabled by default.
- Retains successful and blocked acquisition outcomes under `<storage-root>/historical-acquisition/`.
- Keeps equity acquisition fail-closed and preserves governed CSV import as the fallback.

### Canonical acquisition and handoff

- Parses the Kraken spot OHLC response and rejects provider errors or ambiguous pair payloads.
- Excludes Kraken's final current, not-yet-committed bar from accepted historical evidence.
- Converts completed rows into the canonical timestamp/open/high/low/close/volume contract.
- Routes normalized rows through the existing local OHLCV validation and persistence service.
- Returns the canonical dataset revision ID, Parquet payload, SQLite metadata path, and row count in acquisition evidence.
- Retains the original provider JSON and digest independently from normalized evidence.
- Reuses the same deterministic revision for equivalent provider payloads.
- Rejects malformed or low-quality provider payloads without creating an accepted canonical revision.

The canonical Parquet payload and dataset revision fields now match the input contract consumed by the U8 research pipeline. Full end-to-end manual U8 execution remains an exit-evidence task rather than a new implementation dependency.

## Required command surface

```bash
uv run osca historical-data fetch XBTUSD crypto kraken \
  --timeframe 1d \
  --network-access-enabled \
  --storage-root .osca/manual-test
```

Successful output includes:

- `dataset_revision_id`
- `canonical_payload_uri`
- `canonical_metadata_uri`
- `canonical_row_count`
- raw provider payload lineage and policy findings

Blocked equity evidence can be inspected with:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/manual-test
```

The existing governed CSV import remains the equity fallback.

## Provider admission gate

A provider path is not implementation-ready until the repository records:

- provider and endpoint identity;
- supported asset classes, venues, symbols, intervals, and history limits;
- authentication and credential requirements;
- free-tier or public-use limits;
- attribution requirements;
- retrieval, retention, transformation, export, backup, and redistribution policy;
- timestamp, adjustment, completion, and quality semantics;
- quota and retry behavior;
- raw-payload retention or explicit non-retention evidence;
- health and capability failure behavior;
- golden fixtures and conformance tests.

Licensing or terms uncertainty blocks admission. Convenience alone is not sufficient.

## Remaining U9 implementation and evidence

1. Add durable job-level idempotency and concurrent-request sharing beyond deterministic revision reuse.
2. Add explicit quota and rate-limit outcome classification with retry guidance.
3. Add provider correction and parser-version revision evidence.
4. Prove CSV fallback equivalence with automated coverage.
5. Exercise the canonical Kraken revision through the full U8 pipeline and workspace in manual acceptance.
6. Complete the clean-profile manual acceptance exercise and exit review.

## Security and safety

- Credentials use named secret references and never enter logs, URLs, manifests, payload exports, or portable configuration.
- Network access is limited to admitted provider endpoints.
- No recommendation, model promotion, broker, exchange-order, autonomous-execution, or real-capital capability is introduced.
- Acquisition output is research data, not investment advice.

## Exit criteria

U9 is complete only when:

- at least one no-cost cryptocurrency acquisition path passes;
- one no-cost equity path passes, or is explicitly blocked with retained terms evidence and the provider-neutral/CSV workflow remains complete;
- primary CLI discovery and documentation match behavior;
- canonical provenance, policy, revision, integrity, and quality evidence is retained;
- failure paths are actionable and non-corrupting;
- U8 accepts the resulting revision;
- automated and manual evidence is retained;
- all hosted quality gates pass.
