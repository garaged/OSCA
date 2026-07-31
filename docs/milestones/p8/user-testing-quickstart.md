# P8 User Testing Quickstart

Use this after P8 is merged to get a compact sense of OSCA's current app shape.

## Start from a Clean Checkout

```bash
uv sync --all-groups
```

## Import Local OHLCV Data

```bash
osca local-ohlcv-import tests/fixtures/local_ohlcv/aapl_daily.csv AAPL 1d --storage-root /tmp/osca-p8-smoke
```

Copy the `dataset_revision_id` from the JSON output and use it in the payload path below.

## Run the Demo Research Report

```bash
osca demo-research-report /tmp/osca-p8-smoke/payloads/<dataset-revision-id>.parquet AAPL 1d --output-file /tmp/osca-p8-smoke/demo-research.md
```

## Run the Backtest-to-Paper Evidence Report

```bash
osca backtest-paper-run /tmp/osca-p8-smoke/payloads/<dataset-revision-id>.parquet AAPL 1d --output-file /tmp/osca-p8-smoke/backtest-paper.md
```

## What to Inspect

- JSON output should be readable and evidence-oriented.
- Markdown reports should be created under `/tmp/osca-p8-smoke`.
- The backtest-to-paper output should include strategy metrics and a paper-evaluation record.
- Deferred boundaries should remain false for live providers, live brokers, recommendations, autonomous execution, production ingestion, and real-capital orders.

## Current Product Meaning

After P8, OSCA is usable as a local evidence workflow over user-supplied OHLCV data. It is not yet an analyst workspace, live provider system, scheduler, recommendation engine, or trading system.
