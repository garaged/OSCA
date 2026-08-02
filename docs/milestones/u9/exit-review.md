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
- the U8 experiment, diagnostic, and manifest artifacts;
- validation artifacts when the diagnostic is eligible;
- no recommendations or execution actions.

Exercise the blocked equity path:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/u9-acceptance
```

The expected status is `provider_unavailable`, with CSV fallback guidance and no network use.

## Acceptance checklist

- [x] Real Kraken acquisition succeeds.
- [x] Raw digest and canonical revision are retained.
- [x] Canonical quality findings are acceptable.
- [x] U8 pipeline consumes the exact acquired payload and revision.
- [ ] Workspace discovers the complete evidence chain.
- [x] Blocked equity behavior is explicit and non-networked.
- [x] Recommendation and execution boundaries are false for retained acquisition results.
- [x] Hosted Quality is fully green.
- [x] Final Kraken acquisition and pipeline identifiers and interpretation are recorded below.

## Final retained evidence

### Hosted validation

The latest PR #72 Quality run passed Ruff, strict mypy, all tests and architecture checks, OpenSpec validation, document-link validation, and secret scanning.

### Successful Kraken acquisition

Executed on August 2, 2026 against the clean U9 acceptance storage root.

Observed retained result:

- completed at `2026-08-02T14:05:59.914991Z`;
- provider `kraken` with admission status `approved`;
- asset class `crypto`, symbol `XBTUSD`, timeframe `1d`;
- acquisition status `succeeded`;
- dataset revision `dee68bf2-e8e1-5521-9e93-d2d6dc606bae`;
- canonical payload `.osca/u9-acceptance/payloads/dee68bf2-e8e1-5521-9e93-d2d6dc606bae.parquet`;
- canonical metadata `.osca/u9-acceptance/osca-local-data.sqlite`;
- canonical row count `720`;
- parser version `kraken-ohlc-v1`;
- raw payload `file:///Users/maxvaldez/DEVEL/Playground/OSCA/.osca/u9-acceptance/production-ingestion/kraken/spot_ohlc/04e11941-2d77-438f-97ef-380a4444c821.json`;
- raw payload digest `sha256:13a8a05f68560ef535562d422414e3a04182d90b351dd781ae669e6dab44c71b`;
- acquisition evidence `file:///Users/maxvaldez/DEVEL/Playground/OSCA/.osca/u9-acceptance/historical-acquisition/kraken-crypto-XBTUSD-1d-all-kraken-ohlc-v1.json`;
- findings `internal-use-only`, `redistribution-disabled`, and `current-uncommitted-bar-excluded`;
- redistribution, recommendations, broker execution, and real-capital execution remained disabled.

Interpretation: the admitted Kraken path successfully retained immutable raw evidence, excluded the current uncommitted bar, produced a canonical 720-row OHLCV revision, and preserved every licensing and execution boundary required by U9.

### U8 research-pipeline handoff

The exact acquired canonical payload and revision were submitted to the governed U8 research pipeline.

Observed retained manifest:

- run ID `d2cfcf58-ce0d-4bf9-be04-62ed84abb61d`;
- experiment ID `7de528ca-64d8-4dd8-be44-8458a28c6c50`;
- pipeline family `osca.research-pipeline.manifest`, version `1.0.0`;
- status `diagnostic_not_eligible`;
- diagnostic status `review_required`;
- experiment artifact `.osca/u9-acceptance/research-evidence/d2cfcf58-ce0d-4bf9-be04-62ed84abb61d/experiment.json`;
- diagnostic artifact `.osca/u9-acceptance/research-evidence/d2cfcf58-ce0d-4bf9-be04-62ed84abb61d/diagnostic.json`;
- automatic promotion, recommendations, broker execution, and real-capital execution remained disabled.

Interpretation: the acquired U9 revision was accepted by the U8 pipeline and produced retained experiment and diagnostic evidence. The diagnostic was not eligible for validation, so the pipeline stopped at the human-review boundary and did not create validation artifacts. This is an expected fail-closed outcome and satisfies the U9 handoff requirement; U9 does not require the model evidence to pass the U6 eligibility gate.

### Blocked-equity acceptance

Executed on August 2, 2026 against the same U9 acceptance storage root:

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

Interpretation: the no-cost equity provider boundary failed closed exactly as designed.

### Workspace discovery

Pending confirmation that the analyst workspace discovers the canonical dataset, historical-acquisition evidence, and U8 experiment, diagnostic, and manifest artifacts. Validation artifacts are not expected for this run because the diagnostic was not eligible.

## Exit decision

Pending only workspace-discovery confirmation. Hosted validation, successful real Kraken acquisition, canonical lineage, U8 research handoff, blocked-equity behavior, and all safety-boundary evidence pass. U10 must not weaken the provider, licensing, provenance, or execution boundaries established here.
