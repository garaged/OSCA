# U11 Clean-Profile Manual Acceptance

Run from a clean clone with Python 3.13 and the locked environment.

## 1. Initialize and diagnose

```bash
rm -rf .osca/u11-acceptance

uv sync --locked

uv run osca init \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-init.json

uv run osca doctor \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-doctor-before.json
```

The first doctor result may be `warning` because no retained evidence exists. It must report valid configuration, writable storage, SQLite/PyArrow readiness, loopback port status, admitted Kraken public capability, no credential requirement for the no-cost path, and all recommendation/execution boundaries disabled.

## 2. Acquire or import data

Preferred no-cost network path:

```bash
uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --expected-pair-key XXBTZUSD \
  --minimum-rows 250 \
  --network-access-enabled \
  --storage-root .osca/u11-acceptance/profile/data \
  | tee .osca/u11-acquisition.json
```

Offline fallback:

```bash
uv run osca import-data \
  tests/fixtures/local_ohlcv/aapl_backtest_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/u11-acceptance/profile/data \
  | tee .osca/u11-import.json
```

## 3. Run research through the primary CLI

Use the emitted canonical payload URI and dataset revision:

```bash
uv run osca research-pipeline \
  '<CANONICAL_PAYLOAD_PATH>' \
  '<DATASET_REVISION_ID>' \
  XBTUSD \
  1d \
  --storage-root .osca/u11-acceptance/profile/data \
  --reviewer "$USER" \
  --rationale "Approved for local evidence-only U11 acceptance." \
  --approve-local-validation \
  | tee .osca/u11-research-pipeline.json
```

A diagnostic-ineligible result is acceptable when experiment and diagnostic evidence are retained and validation stops fail-closed.

## 4. Diagnose and inspect the populated profile

```bash
uv run osca doctor \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-doctor-after.json

uv run osca workspace \
  --profile-root .osca/u11-acceptance/profile \
  --snapshot \
  | tee .osca/u11-workspace-snapshot.json
```

The populated doctor result must report evidence consistency without errors. The workspace must discover the canonical dataset and every retained acquisition/pipeline artifact that exists.

## 5. Compatibility equivalence

Confirm the compatibility names remain discoverable and map to the U11 canonical commands:

```bash
uv run osca import-data --help
uv run osca local-ohlcv-import --help
uv run osca analyze --help
uv run osca demo-research-report --help
uv run osca backtest --help
uv run osca backtest-paper-run --help
uv run osca research-pipeline --help
uv run osca-research-pipeline --help
```

Compatibility entry points remain supported through U13 release-candidate acceptance.

## Required retained evidence

Retain and upload:

- `.osca/u11-init.json`
- `.osca/u11-doctor-before.json`
- acquisition or import JSON
- `.osca/u11-research-pipeline.json`
- `.osca/u11-doctor-after.json`
- `.osca/u11-workspace-snapshot.json`

Record identifiers, statuses, warnings, and the safety-boundary interpretation in `exit-review.md` before marking U11 complete.
