# Desktop Development

Status: Active through D2

## Supported development launcher

Run from the repository root:

```bash
uv sync --locked
cd apps/desktop
npm ci
cd ../..
uv run python scripts/run_desktop.py
```

The launcher executes Tauri development mode while setting `OSCA_DESKTOP_PYTHON` to the exact Python interpreter selected by `uv`. This prevents the Rust host from accidentally launching an unrelated system `python3` that does not contain the locked OSCA environment.

## Sidecar selection

The Rust host resolves the Python application process in this order:

1. `OSCA_DESKTOP_SIDECAR`: an explicit packaged sidecar executable; no Python module arguments are appended.
2. `OSCA_DESKTOP_PYTHON`: an explicit Python interpreter used with `-m osca.desktop_api.stdio`.
3. `python3 -m osca.desktop_api.stdio`: compatibility fallback only.

For repository development and hosted package smoke testing, use the supported launcher or set `OSCA_DESKTOP_PYTHON` explicitly. Do not rely on the fallback when validating a release candidate.

## Boundary guarantees

- The sidecar receives one JSON request on standard input and must return exactly one bounded JSON response line.
- Requests and responses are limited to 1 MiB.
- Each request has a 15-second broker timeout.
- Raw sidecar stderr is not returned to the ordinary desktop UI.
- React uses only the allowlisted `desktop_request` command.
- Python remains authoritative for profiles, storage, diagnostics, imports, providers, recommendations, and execution boundaries.

## Direct Tauri usage

Direct invocation is supported only when the interpreter is explicit:

```bash
OSCA_DESKTOP_PYTHON="$(uv run python -c 'import sys; print(sys.executable)')" \
  npm --prefix apps/desktop run tauri dev
```

The root launcher is preferred because it validates the Python baseline, imports the OSCA package before launch, and preserves one documented workflow.
