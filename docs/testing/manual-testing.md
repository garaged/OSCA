# Manual Testing and Usage

- **Status:** Active from M8
- **First covered milestone:** M8 F3 paper evaluation and automation foundation
- **Current coverage:** Through P9 implementation candidate
- **Audience:** Maintainers and early operators
- **Purpose:** Keep executable reality checks for user- and operator-visible behavior while preserving safety boundaries.
- **Last reviewed:** 2026-07-31

## Governance

Every milestone from M8 onward must review this guide when it changes CLI, storage, provider, research, backtest, paper-evaluation, scheduling, recovery, notification, or other operator-visible behavior.

Manual checks supplement but never replace:

- Ruff and strict mypy.
- Automated tests and contract checks.
- Migration, link, and architecture validation.
- OpenSpec strict validation.
- Secret scanning.
- Hosted Quality.

When real behavior differs from documentation, treat the mismatch as product-quality evidence: correct the documentation or implementation and rerun the exact workflow.

## Preparation

1. Start from a clean checkout of the intended `main` or PR head.
2. Use Python 3.13.
3. Recreate or synchronize the environment:

~~~bash
uv sync
uv run ruff check .
uv run mypy src tests
uv run pytest
~~~

4. Use disposable local storage, such as `.osca/manual-test` or `/tmp/osca-manual-test`.
5. Do not configure broker or exchange execution credentials.
6. Do not use real-capital accounts or orders.
7. For provider previews, start with deterministic fixtures before optional network checks.

## Historical milestone coverage

The detailed milestone specifications, exit reviews, tests, and retained evidence remain authoritative for earlier manual-review expectations.

| Milestone range | Manual-review focus | Current boundary |
|---|---|---|
| M8 | Paper-account identity, approved-candidate gates, health controls, pause/kill switch, schedule/recovery evidence, local notification evidence | No live broker or real orders. |
| M9 | Feature/label registries, evaluation reports, promotion gates, drift monitoring, retraining evidence | No runtime trainer or automatic promotion. |
| M10 | LLM routes, prompts, tools, budgets, privacy gates, evaluation evidence | No provider calls, recommendations, or state-changing tools. |
| M11 | Analytical-pack manifests, evidence synthesis, comparison, calibration, portfolio scenarios, visualization metadata | Metadata/evidence foundation, not complete runtime engines. |
| M12 | Backup/restore/DR/health/alert/workflow/risk metadata | No active restore, external delivery, or runtime scheduler. |
| P1-P5 | Provider promotion evidence, no-cost catalog, readiness, fixture contracts, operator state | No live provider calls, credential materialization, routing, or production ingestion. |
| P6 | Local CSV/Parquet OHLCV import, schema validation, Parquet payload, SQLite metadata | Network access remains disabled. |
| P7 | Deterministic local research report and evidence-only framing | No ML/LLM execution or recommendations. |

## P6 local OHLCV import smoke check

~~~bash
uv run osca local-ohlcv-import \
  tests/fixtures/local_ohlcv/aapl_daily.csv \
  AAPL \
  1d \
  --storage-root /tmp/osca-p6-smoke
~~~

Expected:

- SQLite metadata and a Parquet payload are written under the selected storage root.
- Output includes dataset revision, symbol, timeframe, row count, checksum, payload URI, and metadata URI.
- Missing canonical columns, duplicate/non-increasing timestamps, invalid OHLC relationships, and invalid input files fail closed.
- Live providers, credential materialization, runtime routing, production ingestion, and real-capital orders remain disabled.

The three-row `aapl_daily.csv` fixture is valid for import-only smoke testing. Do not use it for the P8 backtest walkthrough.

## P7 deterministic research smoke check

Use the emitted `payload_uri` from a P6 import:

~~~bash
uv run osca demo-research-report \
  "$PAYLOAD_URI" \
  AAPL \
  1d \
  --output-file /tmp/osca-p7-smoke/report.md
~~~

Expected:

- CLI JSON and the Markdown report are produced.
- Evidence includes bar count, first/latest close, total return, mean period return, volatility, max drawdown, SMA 3, and SMA 5.
- The report states evidence-only and not-financial-advice semantics.
- Invalid or incomplete OHLCV payloads fail closed.

## P8 backtest-to-paper happy-path smoke check

The built-in `sma-trend-long-only` strategy requires at least five bars. Use the ten-row fixture and confirm `row_count: 10` before continuing.

~~~bash
rm -rf .osca/manual-test

IMPORT_RESULT="$(uv run osca local-ohlcv-import \
  tests/fixtures/local_ohlcv/aapl_backtest_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/manual-test)"

printf '%s\n' "$IMPORT_RESULT"

PAYLOAD_URI="$(printf '%s\n' "$IMPORT_RESULT" | uv run python -c \
  'import json, sys; print(json.load(sys.stdin)["payload_uri"])')"

printf 'Using payload: %s\n' "$PAYLOAD_URI"
~~~

Stop if the import output does not contain `"row_count": 10`. The emitted `payload_uri` is the source of truth; do not type shell placeholders such as `<dataset-revision-id>`.

Run both evidence reports:

~~~bash
uv run osca demo-research-report \
  "$PAYLOAD_URI" \
  AAPL \
  1d \
  --output-file .osca/manual-test/demo-research.md

uv run osca backtest-paper-run \
  "$PAYLOAD_URI" \
  AAPL \
  1d \
  --initial-cash 10000 \
  --output-file .osca/manual-test/backtest-paper.md
~~~

Expected:

- Both Markdown reports exist.
- Backtest evidence includes strategy identity, bars processed, signal bars, initial/final equity, strategy return, buy-and-hold return, max drawdown, exposure, and evidence-trade count.
- Paper evidence is linked to the backtest and remains `local-evidence-only`.
- Live providers, live brokers, recommendations, autonomous execution, production ingestion, and real-capital orders remain disabled.
- A payload with fewer than five bars fails closed before strategy execution.

The accepted manual validation processed ten AAPL daily bars and produced three simulated evidence trades. See [retained P8 evidence](../../evidence/p8/manual-backtest-paper-report.md) and the [P8 quickstart](../milestones/p8/user-testing-quickstart.md).

## P9 SEC preview and FRED terms-gate smoke check

Use the [P9 user testing quickstart](../milestones/p9/user-testing-quickstart.md) as the executable source of truth.

### Discover the isolated preview CLI

~~~bash
uv run python -m osca.provider_preview --help
~~~

P9 intentionally does not add general runtime provider routing; P10 owns that surface.

### Replay the deterministic SEC fixture

~~~bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --fixture-file tests/fixtures/provider_preview/sec_companyfacts_aapl.json \
  --storage-root .osca/manual-test
~~~

Expected:

- `provider_id: sec_edgar`
- `endpoint: sec_company_facts`
- `mode: fixture_replay`
- `outcome: succeeded`
- `record_count: 3`
- `network_access_used: false`
- `network_access_enabled: false`
- Production ingestion, runtime routing, credential materialization, recommendations, and real-capital orders remain false.

### Confirm SEC network access is fail-closed by default

~~~bash
uv run python -m osca.provider_preview sec-company-facts 320193
~~~

Expected: non-zero exit with an actionable message requiring a fixture path or explicit network access.

### Optional bounded SEC live preview

Replace both placeholders with real identity values; the implementation rejects placeholder identity.

~~~bash
uv run python -m osca.provider_preview sec-company-facts \
  320193 \
  --enable-network \
  --user-agent "YOUR_ORGANIZATION YOUR_CONTACT_EMAIL" \
  --storage-root .osca/manual-test
~~~

Expected:

- Only the approved HTTPS `data.sec.gov` company-facts path is used.
- The first successful request writes a bounded payload and metadata sidecar under `.osca/manual-test/provider-preview/sec-edgar/`.
- Repeating the request returns `outcome: cache_hit` and `network_access_used: false`, unless `--force-refresh` is supplied.
- Provider errors, malformed JSON, oversized content, and unsupported paths fail closed.
- The implementation defaults to two requests per second and rejects configuration above nine requests per second.

### Confirm FRED live use is policy-blocked

~~~bash
uv run python -m osca.provider_preview fred-series GDP \
  --enable-network \
  --secret-reference secret:fred/default
~~~

Expected: intentional non-zero exit after structured evidence containing:

- `mode: policy_blocked`
- `outcome: blocked`
- `network_access_used: false`
- `credential_materialized: false`
- no payload URI or checksum
- findings for prohibited retention and unresolved legal/software-use evidence

No FRED network request is issued, no key is resolved, and no FRED content is cached or archived.

## Provider-state interpretation after P9

| Provider | Contract/readiness meaning |
|---|---|
| SEC EDGAR | Preferred official enrichment source; fixture replay available; opt-in bounded preview implemented in P9. |
| FRED | Preferred official macro candidate; network-disabled fixture contract retained; live readiness is `NEEDS_EVIDENCE`. |
| Alpha Vantage / Nasdaq Data Link | Conditional; exact account-plan, quota, endpoint, and terms evidence required. |
| Stooq | Research-only. |
| Yahoo Finance unofficial paths | Excluded. |
| Twelve Data / Kraken | Governed production-promotion candidates, not enabled by P9. |

## Universal deferred-boundary check

After every manual workflow, confirm no output or documentation claims that OSCA currently provides:

- Authoritative investment recommendations.
- Live broker or exchange connections.
- Autonomous strategy execution.
- Real-capital order placement.
- General production provider routing or ingestion.
- Credential values in logs, URLs, metadata, reports, or portable configuration.

Any discrepancy is a release-blocking documentation or product defect and must be corrected before the milestone is marked complete.
