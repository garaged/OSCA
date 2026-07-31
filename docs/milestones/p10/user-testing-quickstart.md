# P10 User Testing Quickstart

This walkthrough validates capability routing without requiring paid providers, FRED access, or live trading behavior.

## Prerequisites

```bash
uv sync --locked
mkdir -p .osca/manual-p10
```

Use the P8 quickstart first if you do not already have a governed local Parquet payload. The following import command creates one from the ten-bar fixture:

```bash
IMPORT_JSON="$(uv run osca local-ohlcv-import \
  tests/fixtures/local_ohlcv/aapl_backtest_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/manual-p10)"

export PAYLOAD_URI="$(printf '%s' "$IMPORT_JSON" | uv run python -c \
  'import json,sys; print(json.load(sys.stdin)["payload_uri"])')"

printf '%s\n' "$PAYLOAD_URI"
```

Confirm the import JSON reports `row_count: 10` before continuing.

## 1. Inspect the capability matrix

```bash
uv run python -m osca.runtime_routing policy
```

Expected routing policy:

- `ohlcv` selects only `local_ohlcv`.
- `company_facts` and `filings` prefer an explicit SEC fixture before an explicit SEC live preview.
- `macro_series` has no selectable source and reports `policy_blocked` while FRED remains gated.

## 2. Route governed local OHLCV

```bash
uv run python -m osca.runtime_routing local-ohlcv \
  AAPL \
  "$PAYLOAD_URI" \
  --timeframe 1d
```

Expected evidence:

- `status: selected`
- `selected_source: local_ohlcv`
- `network_access_used: false`
- `production_ingestion_enabled: false`
- `recommendations_enabled: false`
- `real_capital_orders_enabled: false`

## 3. Route deterministic SEC company facts

```bash
uv run python -m osca.runtime_routing sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-p10
```

Expected evidence:

- `status: selected`
- `selected_source: sec_edgar_fixture`
- `provider_id: sec_edgar`
- `network_access_used: false`

SEC live preview remains optional and requires the same explicit enablement and declared organization/contact user agent documented in the P9 quickstart.

## 4. Confirm FRED is optional and policy-blocked

The command intentionally returns exit code `2` because no macro payload is selected:

```bash
set +e
uv run python -m osca.runtime_routing macro-series CPIAUCSL
MACRO_EXIT=$?
set -e
printf 'macro exit: %s\n' "$MACRO_EXIT"
```

Expected evidence:

- `status: policy_blocked`
- `provider_id: fred`
- no `selected_source`
- no `payload_uri`
- `network_access_used: false`
- `credential_materialized: false`

`MACRO_EXIT` should be `2`. This is an expected capability result, not a failure of OHLCV, SEC enrichment, backtesting, or the analyst workflow.

## 5. Confirm mixed work continues

```bash
uv run python - <<'PY'
import json
import os
from pathlib import Path

from osca.runtime_routing import (
    RuntimeRouter,
    RuntimeRoutingCapability,
    RuntimeRoutingRequest,
)

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
    storage_root=Path(".osca/manual-p10"),
)
print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
PY
```

Expected batch evidence:

- `outcome: partial`
- `selected_count: 1`
- `policy_blocked_count: 1`
- `non_macro_continued: true`
- the OHLCV decision remains `selected`
- the macro decision remains `policy_blocked`

## Stale-data check

Supplying `--max-age-seconds` causes a payload older than the limit to return `provider_unavailable`. Add `--allow-stale` only when deliberately testing stale evidence; the selected decision must then report `stale: true`.

## Boundaries to verify

P10 does not enable automatic source discovery, FRED live access, paid-provider promotion, production ingestion, real-time streaming, recommendations, brokers, autonomous execution, or real-capital orders.
