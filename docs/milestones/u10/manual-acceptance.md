# U10 Clean-Profile Manual Acceptance

Use the retained U9 acceptance root or another storage root containing one complete acquisition-to-pipeline chain.

## Snapshot and dedicated sections

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --snapshot \
  | tee .osca/u10-workspace-snapshot.json
```

Confirm dedicated `acquisitions`, `experiments`, `diagnostics`, `validations`, and `pipeline_runs` sections. The U9/U8 artifacts must not duplicate under `reports`.

## Filter equivalence

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --snapshot \
  --section experiments \
  --symbol XBTUSD \
  --timeframe 1d \
  | tee .osca/u10-experiments-filter.json
```

Start the loopback workspace on an available port:

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --host 127.0.0.1 \
  --port 0
```

When using an explicitly selected available port, compare `/api/evidence?section=experiments&symbol=XBTUSD&timeframe=1d` with the CLI output. Identifiers, statuses, and counts must agree.

## Detail and lineage

Copy one `item_id` from the experiment section and run:

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --detail-item '<EXPERIMENT_ITEM_ID>' \
  | tee .osca/u10-experiment-detail.json
```

Confirm the detail exposes the retained document and links to applicable acquisition, diagnostic, and pipeline-run evidence. Validation may be absent when the pipeline status is diagnostic-not-eligible.

## Governed portable export

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --export-item '<EXPERIMENT_ITEM_ID>' \
  --output .osca/u10-evidence.zip
```

Inspect `manifest.json` in the ZIP. It must retain included and excluded item identifiers, exclude acquisition evidence whose redistribution flag is false, and contain no secrets or credentials.

## Failure-state acceptance

Create a disposable copy of the storage root and exercise:

- malformed dedicated JSON, expected `corrupt`;
- missing family or required parent identifier, expected `incomplete`;
- unsupported family/version, expected `incompatible` unless a missing parent makes the chain orphaned;
- missing retained parent, expected `orphaned`.

No failure-state exercise may modify the source evidence root.

## Safety checks

The snapshot and detail contracts must continue to report read-only operation. Network retrieval, credential materialization, recommendations, automatic promotion, broker connections, autonomous execution, and real-capital orders remain disabled.

## Retain

Retain the snapshot, filtered output, detail output, portable ZIP manifest, selected item IDs, observed statuses, warnings, and a brief interpretation in `docs/milestones/u10/exit-review.md` before marking U10 complete.
