# P8 User Testing Quickstart

Use this after P8 is merged to get a compact sense of OSCA's current app shape.

## Start from a Clean Checkout

~~~bash
uv sync --all-groups
uv run osca --help
~~~

The project uses Python 3.13. If uv sync cannot find that interpreter, install it once with uv python install 3.13 and rerun the command.

## Import Local OHLCV Data

The import command takes input_file, symbol, and timeframe as positional arguments. Its output includes the exact payload_uri that the next two commands need.

Run the following block as-is. It prints the import result and stores its emitted payload_uri in PAYLOAD_URI, so there is no path or revision ID to type manually.

~~~bash
IMPORT_RESULT="$(uv run osca local-ohlcv-import \
  tests/fixtures/local_ohlcv/aapl_daily.csv \
  AAPL \
  1d \
  --storage-root .osca/manual-test)"

printf '%s\n' "$IMPORT_RESULT"

PAYLOAD_URI="$(printf '%s\n' "$IMPORT_RESULT" | uv run python -c \
  'import json, sys; print(json.load(sys.stdin)["payload_uri"])')"

printf 'Using payload: %s\n' "$PAYLOAD_URI"
~~~

The sample import should report three rows. Its payload_uri is the source of truth for the remaining commands; do not type placeholder text such as <dataset-revision-id> into the shell.

## Run the Demo Research Report

~~~bash
uv run osca demo-research-report \
  "$PAYLOAD_URI" \
  AAPL \
  1d \
  --output-file .osca/manual-test/demo-research.md
~~~

Open the generated report with your operating system's usual file viewer, for example on macOS:

~~~bash
open .osca/manual-test/demo-research.md
~~~

## Run the Backtest-to-Paper Evidence Report

~~~bash
uv run osca backtest-paper-run \
  "$PAYLOAD_URI" \
  AAPL \
  1d \
  --initial-cash 10000 \
  --output-file .osca/manual-test/backtest-paper.md
~~~

Then inspect the evidence report:

~~~bash
open .osca/manual-test/backtest-paper.md
~~~

## What to Inspect

- The import JSON is readable and clearly identifies the local payload it created.
- Both Markdown reports are created under .osca/manual-test.
- The backtest-to-paper output includes strategy metrics and a paper-evaluation record.
- The workflow remains local and evidence-oriented: deferred boundaries stay false for live providers, live brokers, recommendations, autonomous execution, production ingestion, and real-capital orders.
- Commands fail with a clear message if the input file or payload path does not exist.

## Current Product Meaning

After P8, OSCA is usable as a local evidence workflow over user-supplied OHLCV data. It is not yet an analyst workspace, live provider system, scheduler, recommendation engine, or trading system.
