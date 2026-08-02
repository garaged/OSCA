# Manual Testing and Usage

- **Status:** Active from M8
- **First covered milestone:** M8 F3 paper evaluation and automation foundation
- **Current coverage:** Through U9 governed historical acquisition
- **Audience:** Maintainers and early operators
- **Purpose:** Keep executable reality checks for user- and operator-visible behavior while preserving safety boundaries.
- **Last reviewed:** 2026-08-02

## Governance

Every milestone from M8 onward must review this guide when it changes CLI, storage, providers, routing, research, backtesting, paper evidence, scheduling, recovery, notifications, ML diagnostics, model validation, or other operator-visible behavior.

Manual checks supplement but never replace Ruff, strict mypy, automated tests, contract/migration/link/architecture checks, OpenSpec strict validation, secret scanning, and hosted Quality.

When real behavior differs from documentation, treat the mismatch as product-quality evidence and correct the implementation or documentation before completion.

## Preparation

```bash
uv sync --locked
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Use disposable storage such as `.osca/manual-test`. `.osca/` is ignored by Git. Do not configure broker/exchange credentials or real-capital accounts. Start provider workflows with deterministic fixtures.

## Historical coverage

M8-M12, P1-P17, and U2-U8 detailed specifications, exit reviews, tests, and retained evidence remain authoritative. Their boundaries continue to prohibit live execution, ungoverned provider use, credential leakage, investment recommendations, and automatic promotion.

## P6-P8 local evidence workflow

Use the ten-row AAPL fixture for the deterministic smoke workflow:

```bash
rm -rf .osca/manual-test

IMPORT_RESULT="$(uv run osca local-ohlcv-import \
  tests/fixtures/local_ohlcv/aapl_backtest_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/manual-test)"

printf '%s\n' "$IMPORT_RESULT"

export PAYLOAD_URI="$(printf '%s\n' "$IMPORT_RESULT" | uv run python -c \
  'import json,sys; print(json.load(sys.stdin)["payload_uri"])')"
```

Stop unless the import output contains `"row_count": 10`.

```bash
uv run osca demo-research-report \
  "$PAYLOAD_URI" AAPL 1d \
  --output-file .osca/manual-test/demo-research.md

uv run osca backtest-paper-run \
  "$PAYLOAD_URI" AAPL 1d \
  --initial-cash 10000 \
  --output-file .osca/manual-test/backtest-paper.md
```

Expected:

- governed Parquet payload and SQLite metadata
- deterministic research metrics and Markdown report
- transparent `sma-trend-long-only` historical evidence
- buy-and-hold comparison and linked `local-evidence-only` paper record
- no live providers, recommendations, brokers, autonomous execution, or real-capital orders

See the [P8 quickstart](../milestones/p8/user-testing-quickstart.md) and [retained P8 manual evidence](../../evidence/p8/manual-backtest-paper-report.md).

## P9 SEC preview and FRED terms gate

Use the [P9 quickstart](../milestones/p9/user-testing-quickstart.md).

```bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-test
```

Expected: `sec_edgar`, `fixture_replay`, `succeeded`, `record_count: 3`, and no network access.

FRED remains intentionally blocked. An explicit live request must exit nonzero with `policy_blocked` evidence, no network request, no secret resolution, and no payload or cache.

## P10 capability-based routing

Use the [P10 quickstart](../milestones/p10/user-testing-quickstart.md).

```bash
uv run python -m osca.runtime_routing policy
uv run python -m osca.runtime_routing local-ohlcv \
  AAPL "$PAYLOAD_URI" --timeframe 1d
```

Expected:

- local OHLCV is the selected market-history source
- SEC fixture routing remains available for enrichment
- macro requests fail closed as `policy_blocked` or `provider_unavailable`
- no production provider, credential, broker, or real-capital boundary is enabled

## U2-U7 analytical and ML modules

The standalone module entry points remain supported for focused testing:

```bash
uv run python -m osca.analytical_data --help
uv run python -m osca.quantitative_analysis --help
uv run python -m osca.ml_experiments --help
uv run python -m osca.prediction_lab --help
uv run python -m osca.model_validation --help
uv run python -m osca.analyst_workspace --help
```

For classification, the accepted governed values are:

- task: `classification`
- model: `logistic_classification`

A U5 experiment must retain point-in-time-safe predictions and keep network, credential, recommendation, automatic-promotion, broker, and real-capital boundaries disabled. U6 may classify the evidence as eligible for U7, but eligibility is not a claim of predictive or investment quality. U7 requires explicit human approval and must compare cost-aware model-derived evidence with buy-and-hold.

## U8 guided real-world research workflow

Use at least 250 governed daily bars for a meaningful workflow. The August 1, 2026 validation used 1,255 AAPL daily bars and demonstrated that an eligible model can still materially underperform buy-and-hold.

After importing the CSV, obtain the payload URI and dataset revision from the import JSON, then run the primary CLI command:

```bash
uv run osca research-pipeline \
  "$PAYLOAD_URI" \
  "$DATASET_REVISION_ID" \
  AAPL \
  1d \
  --storage-root .osca/manual-test \
  --reviewer "$USER" \
  --rationale "Approved for local evidence-only validation after reviewing the retained experiment and diagnostics." \
  --approve-local-validation
```

Expected:

- task `classification`
- model `logistic_classification`
- experiment and U6 diagnostic retained under `.osca/manual-test/research-evidence/<run-id>/`
- U7 request/result retained only when the diagnostic is eligible
- a traceable `manifest.json` records artifact paths, status, evidence digest, and safety boundaries
- noneligible diagnostics fail closed before U7 while preserving experiment and diagnostic evidence
- no live serving, automatic promotion, recommendation, broker, or real-capital path is enabled

The explicit `--approve-local-validation` option records human authorization for local evidence comparison only. It is not an investment approval and does not authorize paper-challenger designation, broker connectivity, or orders.

See the [U8 real-world quickstart](../milestones/u8/real-world-research-quickstart.md).

## U9 governed historical acquisition

Use a clean storage root:

```bash
rm -rf .osca/u9-acceptance
```

### Successful Kraken acquisition

```bash
uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --expected-pair-key XXBTZUSD \
  --minimum-rows 250 \
  --network-access-enabled \
  --storage-root .osca/u9-acceptance \
  | tee .osca/u9-acceptance-acquisition.json
```

Confirm the result exposes and retains:

- `request_id`, `correlation_id`, `job_id`, and `acquisition_id`
- admitted provider, venue context, and verified provider pair key
- raw payload URI and SHA-256
- normalized SHA-256
- parser and normalizer versions
- job progress, attempts, duration, and completion state
- immutable dataset revision, Parquet payload, SQLite metadata, and row count
- predecessor/supersession fields when a parser or correction changes the revision
- attribution, internal-use limitation, and disabled redistribution/execution flags

### Bounded range and mapping checks

Repeat with explicit UTC timestamps appropriate for the retained Kraken window:

```bash
uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --start-at 2024-08-01T00:00:00Z \
  --end-at 2024-08-03T00:00:00Z \
  --expected-pair-key XXBTZUSD \
  --require-complete-range \
  --network-access-enabled \
  --storage-root .osca/u9-range
```

Confirm rows are restricted to the half-open interval `[start_at, end_at)`. An incorrect `--expected-pair-key` must produce `invalid` without a canonical revision.

### Durable lifecycle, reuse, and cancellation

Re-run the identical successful request. Confirm the canonical revision is reused and `reuse_state` is `reused` without a second accepted revision.

Exercise pre-network cancellation:

```bash
uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --cancel-requested \
  --storage-root .osca/u9-cancel
```

Expected: `cancelled`, a retained job record, no provider payload, and remediation to resubmit without cancellation. Automated coverage also rewrites an interrupted job to `running` and proves the next invocation enters recovery.

### Quota, outage, malformed, partial, and stale checks

The following failure cases are executed with deterministic injected transports in `tests/test_u9_historical_acquisition.py` because public provider failures cannot be triggered reliably or safely on demand:

- Kraken rate-limit error → `quota_blocked`, `quota_state: exhausted`, retry metadata
- Kraken service error → `provider_unavailable`
- non-JSON body → `corrupt`
- structurally invalid Kraken body → `invalid`
- fewer than `minimum_rows` → `partial`
- data older than `freshness_max_age_seconds` → `stale`

Retain the hosted Quality run and focused test names as the acceptance evidence for these deterministic failure scenarios. Operator remediation must be present for every non-success status.

### Blocked equity source

```bash
uv run osca historical-data fetch \
  AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/u9-acceptance
```

Expected: `policy_blocked`, no network-derived payload or canonical revision, explicit CSV fallback guidance, and all recommendation/execution flags false.

### U8 handoff

Use the exact acquired `canonical_payload_uri` and `dataset_revision_id`:

```bash
uv run osca research-pipeline \
  "$CANONICAL_PAYLOAD_URI" \
  "$DATASET_REVISION_ID" \
  XBTUSD \
  1d \
  --storage-root .osca/u9-acceptance \
  --reviewer "$USER" \
  --rationale "Approved for local evidence-only U9 acceptance." \
  --approve-local-validation
```

A `diagnostic_not_eligible` result is valid when experiment and diagnostic artifacts are retained and the pipeline fails closed before validation.

### Workspace discovers the complete evidence chain

This is an explicit U9 acceptance requirement.

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --snapshot \
  | tee .osca/u9-workspace-snapshot.json
```

Confirm the snapshot discovers all artifacts that exist for the run:

- canonical dataset revision from SQLite
- retained historical-acquisition evidence
- persisted acquisition job evidence
- U8 pipeline manifest
- experiment
- diagnostic
- validation request/result only when diagnostic eligibility permitted U7

Also confirm:

- workspace is read-only
- network access and credential materialization are disabled
- recommendations, automatic promotion, broker execution, and real-capital execution remain disabled
- no artifact is silently omitted because it is nested below `historical-acquisition/` or `research-evidence/`

The focused regression `test_workspace_discovers_complete_u9_evidence_chain` is mandatory and complements this clean-profile snapshot.

## Analyst workspace server verification

Start the read-only workspace against the same storage root. Prefer a free dynamic port when running automated tests to avoid accidentally testing another local service.

```bash
PORT="$(uv run python - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)"

uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --host 127.0.0.1 \
  --port "$PORT"
```

Verify:

- `/health` returns `status: ok`, read-only mode, network disabled, and promotion/broker boundaries disabled
- `/` renders the OSCA Analyst Workspace title and safety footer
- `/api/workspace` lists the governed dataset and retained U8/U9 evidence
- `/api/model-validation/run` reproduces deterministic CLI evidence when given the same retained request; only the generated validation ID may differ

## Provider-state interpretation

| Provider/source | Current meaning |
|---|---|
| Governed local OHLCV | Selectable market-history source. |
| Kraken public spot OHLC | Admitted U9 no-cost crypto acquisition for internal use; redistribution disabled. |
| Twelve Data equity | Not admitted; `policy_blocked` with CSV fallback. |
| SEC EDGAR | Fixture and explicit bounded live-preview enrichment source. |
| FRED | Optional macro candidate; live use remains `policy_blocked`. |
| Unconfigured source | `provider_unavailable` or `policy_blocked` according to admission state. |
| Other catalog providers | Retain P1-P5 dispositions and evidence gates. |

## Universal deferred-boundary check

After every workflow, confirm no output or documentation claims that OSCA currently provides:

- authoritative investment recommendations
- live broker or exchange connections
- autonomous strategy execution
- real-capital order placement
- automatic model promotion or live serving
- automatic provider discovery or silent source blending
- scheduled production provider ingestion
- credential values in logs, URLs, metadata, reports, or portable configuration

Any discrepancy is release-blocking.
