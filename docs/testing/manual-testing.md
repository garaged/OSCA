# Manual Testing and Usage

- **Status:** Active from M8
- **First covered milestone:** M8 F3 paper evaluation and automation foundation
- **Current coverage:** Through P10 implementation candidate
- **Audience:** Maintainers and early operators
- **Purpose:** Keep executable reality checks for user- and operator-visible behavior while preserving safety boundaries.
- **Last reviewed:** 2026-07-31

## Governance

Every milestone from M8 onward must review this guide when it changes CLI, storage, providers, routing, research, backtesting, paper evidence, scheduling, recovery, notifications, or other operator-visible behavior.

Manual checks supplement but never replace Ruff, strict mypy, automated tests, contract/migration/link/architecture checks, OpenSpec strict validation, secret scanning, and hosted Quality.

When real behavior differs from documentation, treat the mismatch as product-quality evidence and correct the implementation or documentation before completion.

## Preparation

```bash
uv sync --locked
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Use disposable storage such as `.osca/manual-test`. Do not configure broker/exchange credentials or real-capital accounts. Start provider workflows with deterministic fixtures.

## Historical coverage

M8-M12 and P1-P5 detailed specifications, exit reviews, tests, and retained evidence remain authoritative. Their boundaries continue to prohibit live execution, ungoverned provider use, credential leakage, and automatic promotion.

## P6-P8 local evidence workflow

Use the ten-row AAPL fixture for any workflow that reaches the P8 strategy:

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

Deterministic fixture replay:

```bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-test
```

Expected: `sec_edgar`, `fixture_replay`, `succeeded`, `record_count: 3`, and no network access.

Optional SEC live preview requires explicit `--enable-network` plus a real organization/contact user agent and inherits approved-host/path, throttling, timeout, response-size, cache, and provenance controls.

FRED remains intentionally blocked:

```bash
set +e
uv run python -m osca.provider_preview fred-series GDP \
  --enable-network \
  --secret-reference secret:fred/default
FRED_EXIT=$?
set -e
```

Expected: exit `2`, `policy_blocked`/`blocked` evidence, no network request, no secret resolution, and no payload or cache.

## P10 capability-based routing

Use the [P10 quickstart](../milestones/p10/user-testing-quickstart.md) as the executable source of truth.

### Inspect policy

```bash
uv run python -m osca.runtime_routing policy
```

Expected:

- OHLCV source precedence: `local_ohlcv`
- company facts/filings: SEC fixture before SEC live preview
- macro series: no selectable source; missing-source status `policy_blocked`

### Route local OHLCV

```bash
uv run python -m osca.runtime_routing local-ohlcv \
  AAPL "$PAYLOAD_URI" --timeframe 1d
```

Expected: `selected`, `local_ohlcv`, no network use, and all production/trading boundaries false.

### Route SEC fixture enrichment

```bash
uv run python -m osca.runtime_routing sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-test
```

Expected: `selected`, `sec_edgar_fixture`, no network use.

### Confirm macro independence

```bash
set +e
uv run python -m osca.runtime_routing macro-series CPIAUCSL
MACRO_EXIT=$?
set -e
```

Expected: exit `2`, `status: policy_blocked`, `provider_id: fred`, no selected source, no payload, no network use, and no credential materialization.

A request for an unconfigured macro provider must instead return `provider_unavailable`.

### Confirm partial batch continuation

```bash
uv run python - <<'PY'
import json
import os
from pathlib import Path
from osca.runtime_routing import RuntimeRouter, RuntimeRoutingCapability, RuntimeRoutingRequest

result = RuntimeRouter().route_many(
    (
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.OHLCV,
            resource_id="AAPL",
            local_payload_uri=os.environ["PAYLOAD_URI"],
        ),
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.MACRO_SERIES,
            resource_id="CPIAUCSL",
        ),
    ),
    storage_root=Path(".osca/manual-test"),
)
print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
PY
```

Expected: `outcome: partial`, one selected decision, one policy-blocked decision, and `non_macro_continued: true`.

### Stale check

Use `--max-age-seconds` to make old evidence fail closed as `provider_unavailable`. Add `--allow-stale` only deliberately; the selected decision must report `stale: true` and a stale-source finding.

## Provider-state interpretation

| Provider/source | Current meaning |
|---|---|
| Governed local OHLCV | Selectable P10 market-history source. |
| SEC EDGAR | Fixture and explicit bounded live-preview enrichment source. |
| FRED | Optional macro candidate; live use remains `policy_blocked`. |
| Unconfigured macro source | `provider_unavailable`. |
| Twelve Data / Kraken | Production-promotion candidates, not enabled runtime sources. |
| Other catalog providers | Retain P1-P5 dispositions and evidence gates. |

## Universal deferred-boundary check

After every workflow, confirm no output or documentation claims that OSCA currently provides:

- authoritative investment recommendations
- live broker or exchange connections
- autonomous strategy execution
- real-capital order placement
- automatic provider discovery or silent source blending
- scheduled production provider ingestion
- credential values in logs, URLs, metadata, reports, or portable configuration

Any discrepancy is release-blocking.
