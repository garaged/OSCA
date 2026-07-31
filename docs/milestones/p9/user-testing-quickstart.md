# P9 User Testing Quickstart

Use this after checking out PR #52 or after P9 is merged. Start with fixture replay. Live SEC access is optional and must use your real organization/contact identity.

## Prepare the Python 3.13 environment

~~~bash
uv sync
uv run ruff check .
uv run mypy src tests
uv run pytest
~~~

## Inspect the module CLI

~~~bash
uv run python -m osca.provider_preview --help
~~~

The P9 surface is intentionally isolated from P10 runtime routing. It does not alter the existing local OHLCV, research, or backtest commands.

## Replay the deterministic SEC fixture

~~~bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-test
~~~

Expected evidence:

- `provider_id` is `sec_edgar`.
- `endpoint` is `sec_company_facts`.
- `mode` is `fixture_replay`.
- `outcome` is `succeeded`.
- `record_count` is `3`.
- `network_access_used` and `network_access_enabled` are `false`.
- Production ingestion, runtime routing, recommendations, credential materialization, and real-capital orders remain `false`.

## Confirm network access fails closed by default

~~~bash
uv run python -m osca.provider_preview sec-company-facts 320193
~~~

The command must exit non-zero and explain that a fixture path or explicit network access is required.

## Optional SEC live preview

Only run this when network access is appropriate. Replace both identity fields with real values that identify you or your organization and a monitored contact address.

~~~bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --enable-network \
  --user-agent "YOUR_ORGANIZATION YOUR_CONTACT_EMAIL" \
  --storage-root .osca/manual-test
~~~

Do not paste the command unchanged: placeholder identity is intentionally invalid.

Expected behavior:

- The request uses only the approved `https://data.sec.gov` company-facts endpoint.
- The first successful request writes a bounded payload and metadata sidecar under `.osca/manual-test/provider-preview/sec-edgar/`.
- Repeating the same command returns `outcome: cache_hit` and `network_access_used: false` unless `--force-refresh` is supplied.
- HTTP errors, malformed JSON, oversized responses, and unsupported endpoints fail closed.

The implementation defaults to two requests per second and rejects configuration above nine requests per second, remaining below the SEC's published maximum of ten.

## Confirm FRED is policy-blocked

~~~bash
uv run python -m osca.provider_preview fred-series GDP \
  --enable-network \
  --secret-reference secret:fred/default
~~~

This command intentionally exits non-zero after printing structured evidence. Expected fields include:

- `mode: policy_blocked`
- `outcome: blocked`
- `network_access_used: false`
- `credential_materialized: false`
- no `payload_uri`
- findings for prohibited retention and unresolved legal/software-use evidence

No FRED API key is read or resolved, and no FRED content is requested, cached, or archived.

## Safety meaning

P9 provides enrichment preview evidence only. It does not provide OHLCV data, provider routing, scheduled ingestion, investment recommendations, broker integration, autonomous execution, or real-capital orders.
