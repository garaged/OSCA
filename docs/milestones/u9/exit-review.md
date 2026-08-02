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
- [x] Blocked equity behavior is explicit and non-networked.
- [x] Recommendation and execution boundaries are false for the retained blocked-equity result.
- [x] Hosted Quality is fully green.
- [ ] Final Kraken evidence identifiers and interpretation are added below.

## Final retained evidence

### Hosted validation

The latest PR #72 Quality run passed Ruff, strict mypy, all tests and architecture checks, OpenSpec validation, document-link validation, and secret scanning.

### Blocked-equity acceptance

Executed on August 2, 2026 against a clean U9 acceptance storage root:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/u9-acceptance
```

Observed retained result:

- completed at `2026-08-02T14:07:52.130107Z`;
- provider `twelve_data`;
- asset class `equity`;
- symbol `AAPL`;
- timeframe `1d`;
- admission status `needs_evidence`;
- acquisition status `provider_unavailable`;
- no dataset revision, canonical payload, metadata, or raw provider payload was created;
- findings `equity-provider-not-admitted` and `csv-import-remains-supported`;
- retained evidence URI `file:///Users/maxvaldez/DEVEL/Playground/OSCA/.osca/u9-acceptance/historical-acquisition/twelve_data-equity-AAPL-1d-all-kraken-ohlc-v1.json`;
- rationale directs the operator to governed CSV import;
- redistribution, recommendations, broker execution, and real-capital execution remained disabled.

Interpretation: the no-cost equity provider boundary failed closed exactly as designed. This evidence does not establish the successful Kraken acquisition, canonical revision, U8 pipeline handoff, or workspace-discovery legs.

### Kraken acquisition and research handoff

Pending the retained output identifiers from the real Kraken acquisition, U8 pipeline run, and workspace verification.

## Exit decision

Pending. The blocked-equity and hosted-validation legs pass, but U9 may be marked complete only after the successful real Kraken acquisition, canonical lineage, U8 research handoff, and workspace-discovery evidence are recorded. U10 must not weaken the provider, licensing, provenance, or execution boundaries established here.
