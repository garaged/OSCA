# U9 Exit Review

- **Milestone:** U9 governed no-cost historical data acquisition
- **Status:** Completion candidate
- **Implementation PR:** #72
- **Required final evidence:** hosted Quality plus clean-profile manual acceptance

## Outcome under review

U9 provides a first-class governed historical acquisition path for Kraken public spot OHLC and an explicit blocked-equity decision with governed CSV fallback.

A successful Kraken request retains:

- provider admission and endpoint evidence;
- immutable raw JSON and SHA-256 digest;
- parser identity;
- completed canonical OHLCV rows;
- deterministic dataset revision identity;
- Parquet payload and SQLite metadata;
- source attribution and internal-use limitations;
- recommendation and execution boundaries.

## Provider disposition

| Provider | U9 status | Rationale |
|---|---|---|
| Kraken public spot OHLC | admitted | Public no-key endpoint, personal/internal use, bounded retention and no redistribution |
| Twelve Data | needs evidence | Free Basic material does not establish OSCA's full display, retention, export, backup, and redistribution boundary |
| Alpha Vantage | needs evidence | Exact account-plan and intended-use evidence is insufficient |
| Nasdaq Data Link | needs evidence | Rights are dataset and order-form specific |
| FRED | policy blocked | Existing retention and software/AI-use concerns remain unresolved |

No unavailable equity provider is silently called or treated as admitted.

## Automated evidence expected

Hosted validation must demonstrate:

- Ruff passes.
- Strict mypy passes.
- All tests pass, including U9 acquisition and U9-to-U8 handoff tests.
- OpenSpec strict validation passes.
- Document links and architecture checks pass.
- Secret scanning passes.

The focused U9 tests cover:

- explicit network enablement;
- immutable raw lineage;
- canonical validation and persistence;
- exclusion of Kraken's uncommitted final bar;
- durable completed-result reuse;
- concurrent equivalent-request sharing;
- parser-version revision changes;
- rate-limit retry guidance;
- malformed payload failure without canonical acceptance;
- CSV canonical row equivalence;
- acquired revision compatibility with the U8 research pipeline;
- disabled recommendation, broker, and real-capital boundaries.

## Clean-profile manual procedure

Use a new storage root and a real Kraken public pair.

```bash
rm -rf .osca/u9-acceptance

uv run osca historical-data fetch XBTUSD crypto kraken \
  --timeframe 1d \
  --network-access-enabled \
  --storage-root .osca/u9-acceptance \
  | tee .osca/u9-acceptance-acquisition.json
```

From the output, record:

- `dataset_revision_id`;
- `canonical_payload_uri`;
- `canonical_metadata_uri`;
- `canonical_row_count`;
- `raw_payload_uri`;
- `raw_payload_sha256`;
- `parser_version`;
- findings and safety flags.

Run the human-gated U8 path using those exact values:

```bash
uv run osca research-pipeline \
  <CANONICAL_PAYLOAD_URI> \
  <DATASET_REVISION_ID> \
  XBTUSD \
  1d \
  --storage-root .osca/u9-acceptance \
  --reviewer maxvaldez \
  --rationale "Approved for local evidence-only U9 acceptance." \
  --approve-local-validation \
  | tee .osca/u9-acceptance-pipeline.json
```

Start the analyst workspace on an available loopback port using the documented workspace command, then confirm that the storage root exposes:

- the canonical dataset revision;
- retained historical-acquisition evidence;
- the U8 experiment, diagnostic, manifest, and validation artifacts;
- no recommendations or execution actions.

Exercise the blocked equity path:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/u9-acceptance
```

The expected status is `provider_unavailable`, with CSV fallback guidance and no network use.

## Acceptance checklist

- [ ] Real Kraken acquisition succeeds.
- [ ] Raw digest and canonical revision are retained.
- [ ] Canonical quality findings are acceptable.
- [ ] U8 pipeline consumes the exact acquired payload and revision.
- [ ] Workspace discovers the complete evidence chain.
- [ ] Blocked equity behavior is explicit and non-networked.
- [ ] Recommendation and execution boundaries are false.
- [ ] Hosted Quality is fully green.
- [ ] Final evidence identifiers and interpretation are added below.

## Final retained evidence

Pending execution after PR #72 validation.

## Exit decision

Pending. U9 may be marked complete only after the automated and manual acceptance evidence above is recorded. U10 must not weaken the provider, licensing, provenance, or execution boundaries established here.
