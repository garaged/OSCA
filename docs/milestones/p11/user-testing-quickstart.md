# P11 User Testing Quickstart

## Purpose

Validate the read-only analyst workspace against retained local OSCA evidence.

## Prepare

Use Python 3.13 and synchronize the repository environment:

```bash
uv sync
```

Choose the storage root that contains your P6-P10 artifacts. The examples use `.osca/manual-test` from the P8-P10 walkthroughs.

## Inspect the snapshot first

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/manual-test \
  --snapshot
```

Expected:

- JSON contains all sections: `projects`, `watchlists`, `datasets`, `reports`, `backtests`, `enrichment`, and `routing`.
- `read_only` is `true`.
- Network, credential materialization, production ingestion, recommendations, broker connections, and real-capital orders are `false`.
- Missing sections remain present with an `empty_message`.
- Existing local datasets and reports appear without being rewritten.
- Any retained P10 `policy_blocked` or `provider_unavailable` status remains visible.

## Start the local workspace

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/manual-test \
  --host 127.0.0.1 \
  --port 8000
```

Open `http://127.0.0.1:8000/` in a browser.

Expected:

- The page shows a card for each workspace section.
- A loading state appears briefly before API data is rendered.
- Empty sections show their empty message.
- Available items show title, summary, and status.
- Warnings and policy blocks are visible rather than hidden.
- The footer states that recommendations, credentials, broker connections, and execution are not provided.

## Inspect the JSON API

In another terminal:

```bash
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/api/workspace
curl --fail http://127.0.0.1:8000/api/workspace/datasets
curl --fail http://127.0.0.1:8000/api/workspace/routing
```

Expected:

- `/health` reports `read_only: true` and `network_access_enabled: false`.
- `/api/workspace` returns the complete snapshot.
- Section endpoints return only the requested section.
- An unknown section returns HTTP 404.
- Mutation methods such as `POST /api/workspace` return HTTP 405.

## Confirm loopback enforcement

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/manual-test \
  --host 0.0.0.0
```

Expected: startup exits non-zero and explains that P11 permits only loopback hosts.

## Stop the server

Press `Ctrl-C` in the server terminal.

## Boundaries

P11 does not create or edit projects/watchlists, import data, run reports or backtests, call SEC/FRED, resolve credentials, produce recommendations, connect to brokers, or place orders.
