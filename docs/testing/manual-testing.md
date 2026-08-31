# Manual Testing and Usage

- **Status:** Active from M8
- **First covered milestone:** M8 F3 paper evaluation and automation foundation
- **Current coverage:** Through D8 virtual-portfolio accounting and the desktop acceptance automation foundation
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

## Desktop acceptance policy and human-review smoke test

Repeated desktop acceptance is automated by a deterministic, disposable D5--D7 profile. It uses only bundled synthetic AAPL/MSFT daily data, the typed desktop application-service boundary, and local profile storage. It never enables network access, provider credentials, recommendations, broker connections, autonomous execution, or real-capital operations.

Run the automated baseline and create the review-ready profile:

```bash
make acceptance-check
make acceptance-seed
make acceptance-run
```

`make acceptance-seed` intentionally resets only `.osca/desktop-acceptance`, then retains `evidence/acceptance-manifest.json`. The manifest records the two imported samples, D5 comparison, D7 strategy/backtest/sensitivity/walk-forward results, and D6 project pin. It is the reproducible evidence source for checks that previously required repetitive manual setup.

For a normal desktop milestone, human review is limited to this 5--10 minute smoke test:

1. Open the deterministic profile shown by `make acceptance-info`.
2. In Workbench, inspect the AAPL/MSFT comparison and confirm chart/table readability, selection feedback, and no visual clipping at the target platform's normal and large text size.
3. In Projects and Strategy Lab, confirm the seeded project/pin, backtest result, and evaluation disclosures are understandable and visually coherent.
4. Check keyboard focus, pointer interaction, and permanent safety disclosures for the changed surface only.
5. Record only PASS/FAIL and a screenshot or concise finding for human-judgment issues.

Do not replay the historical D5--D7 procedures unless the change touches their behavior. Re-run their automated coverage instead. Full exploratory/platform acceptance remains required for release candidates, migrations, desktop-shell changes, packaging changes, or a material interaction redesign.

Every milestone acceptance plan must classify each check as one of:

- **Automated** — deterministic invariant, error case, persistence/replay result, export, protocol, or source-boundary behavior. It must name its test/gate and is not re-performed manually when that gate is green.
- **Human judgment** — visual hierarchy, copy, discoverability, chart/table readability, keyboard focus, pointer behavior, and platform rendering. This is the normal 5--10 minute changed-surface smoke path.
- **Exploratory** — a deliberately selected risk probe such as migration/recovery, platform packaging, concurrency, or a material interaction redesign. It is required only when its trigger applies.

The acceptance record must state the exact source revision, platform, automated gates, human-judgment PASS/FAIL, exploratory triggers exercised or waived, findings, and retained screenshots only when they add evidence. A repeated manual step must be promoted to deterministic coverage before the next milestone rather than copied forward as release ritual.

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

Use a clean storage root and follow the complete [U9 acceptance procedure](../milestones/u9/exit-review.md). The accepted path acquires Kraken XBTUSD daily history, retains raw and canonical lineage, runs the U8 research pipeline, verifies the blocked-equity fallback, and confirms workspace discovery.

The U9 output must retain request/job/acquisition identities, verified pair mapping, raw and normalized digests, parser and normalizer versions, canonical revision metadata, explicit degraded statuses, remediation, and disabled recommendation/execution boundaries.

## U10 research-evidence workspace

Use the retained U9 acceptance root and follow the [U10 clean-profile acceptance procedure](../milestones/u10/manual-acceptance.md).

The essential checks are:

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --snapshot \
  | tee .osca/u10-workspace-snapshot.json

uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --snapshot \
  --section experiments \
  --symbol XBTUSD \
  --timeframe 1d \
  | tee .osca/u10-experiments-filter.json
```

Copy the experiment `item_id` from the filtered output:

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --detail-item '<EXPERIMENT_ITEM_ID>' \
  | tee .osca/u10-experiment-detail.json

uv run python -m osca.analyst_workspace \
  --storage-root .osca/u9-acceptance \
  --export-item '<EXPERIMENT_ITEM_ID>' \
  --output .osca/u10-evidence.zip
```

Confirm dedicated sections, complete applicable lineage, explicit unhealthy-artifact states, CLI/API/export agreement, provider-policy exclusions, secret exclusion, read-only operation, and disabled recommendation/execution boundaries.

## U11 first-run and unified operator experience

Follow the [U11 clean-profile acceptance procedure](../milestones/u11/manual-acceptance.md). The canonical flow must use only the primary `osca` CLI:

```bash
rm -rf .osca/u11-acceptance

uv run osca init \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-init.json

uv run osca doctor \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-doctor-before.json
```

Then acquire admitted Kraken history with explicit network opt-in or use the offline fallback:

```bash
uv run osca import-data \
  tests/fixtures/local_ohlcv/aapl_backtest_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/u11-acceptance/profile/data \
  | tee .osca/u11-import.json
```

Use the resulting canonical payload and revision with `osca research-pipeline`, then verify the populated profile:

```bash
uv run osca doctor \
  --profile-root .osca/u11-acceptance/profile \
  | tee .osca/u11-doctor-after.json

uv run osca workspace \
  --profile-root .osca/u11-acceptance/profile \
  --snapshot \
  | tee .osca/u11-workspace-snapshot.json
```

Confirm:

- configuration is versioned and strictly rejects unknown or unsafe fields
- doctor covers Python, PyArrow, SQLite, writable storage, loopback port, provider capability, credentials, and evidence consistency
- the canonical path does not require hand-authored JSON or internal module commands
- `import-data`, `analyze`, and `backtest` remain equivalent to their compatibility entry points
- compatibility names remain available through U13
- workspace is loopback-only and read-only
- network access is explicit, never implicit
- recommendations, automatic promotion, brokers, autonomous execution, and real-capital orders remain disabled

## Analyst workspace server verification

Start the read-only workspace through the U11 primary command:

```bash
uv run osca workspace --profile-root .osca/u11-acceptance/profile
```

Verify `/health`, `/`, `/api/workspace`, `/api/evidence`, one detail endpoint, raw JSON download, and portable export. API and CLI must return the same item identifiers and statuses for equivalent filters.

## Provider-state interpretation

| Provider/source | Current meaning |
|---|---|
| Governed local OHLCV | Selectable market-history source. |
| Kraken public spot OHLC | Admitted U9 no-cost crypto acquisition for internal use; redistribution disabled. |
| Twelve Data equity | Not admitted; `policy_blocked` with CSV/Parquet fallback. |
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
