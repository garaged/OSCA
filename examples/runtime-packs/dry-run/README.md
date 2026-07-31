# OSCA Dry-Run Runtime Pack

This committed example exercises the P15 trusted-local extension lifecycle without external providers, credentials, network access, or financial behavior.

## Prepare the pack

The preparation helper makes `run.py` executable and writes `osca-pack.json` with the current SHA-256 digest.

```bash
python examples/runtime-packs/dry-run/prepare.py
```

Run this command again after editing `run.py` so the manifest digest stays current.

## Validate

```bash
uv run python -m osca.runtime_extensions validate \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-dry-run
```

Expected status: `validated`.

## Prove execution is disabled by default

```bash
uv run python -m osca.runtime_extensions run \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-dry-run \
  --input '{"symbol":"AAPL"}'
```

Expected status: `policy_blocked` with the `execution-disabled` finding.

## Execute explicitly

```bash
uv run python -m osca.runtime_extensions run \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-dry-run \
  --input '{"symbol":"AAPL"}' \
  --enable
```

Expected status: `succeeded`. The retained JSON output echoes the input and reports both runtime markers as `disabled`:

```json
{
  "input": {"symbol": "AAPL"},
  "network": "disabled",
  "ok": true,
  "pack": "osca-dry-run",
  "secrets": "disabled"
}
```

## Install

```bash
uv run python -m osca.runtime_extensions install \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-dry-run
```

The installed version is retained under:

```text
.osca/p15-dry-run/runtime-extensions/osca-dry-run/1.0.0/
```

This pack performs no market analysis. It exists only to validate the extension lifecycle and evidence path.
