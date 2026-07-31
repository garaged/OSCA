# P15 User Testing Quickstart

Use only local packs you trust. P15 is not a hostile-code sandbox.

## Prepare the committed dry-run pack

```bash
rm -rf .osca/p15-manual
python examples/runtime-packs/dry-run/prepare.py
```

The helper makes the example executable and writes `osca-pack.json` with the current SHA-256 digest. Run it again after editing `run.py`.

## Validate

```bash
uv run python -m osca.runtime_extensions validate \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-manual
```

Expected: `validated`, exact package/version and digest, and no process execution.

## Confirm execution is disabled by default

```bash
uv run python -m osca.runtime_extensions run \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-manual \
  --input '{"symbol":"AAPL"}'
```

Expected: `policy_blocked` and `execution-disabled`.

## Execute explicitly

```bash
uv run python -m osca.runtime_extensions run \
  examples/runtime-packs/dry-run \
  --storage-root .osca/p15-manual \
  --input '{"symbol":"AAPL"}' \
  --enable
```

Expected: `succeeded`, exit code `0`, retained stdout/stderr URIs, and output under `.osca/p15-manual/runtime-extensions/osca-dry-run/evidence/`.

The output echoes the input and reports both runtime markers as disabled:

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
  --storage-root .osca/p15-manual
```

Expected: `installed`, a versioned package directory, and an `active.json` pointer.

## Negative checks

- Change one byte in `run.py` after preparing the pack; validation must fail with digest mismatch.
- Change `trust_tier` to `untrusted`; validation must return `policy_blocked`.
- Change `osca_min_version` to `9.0.0`; validation must return `incompatible`.
- Add a manifest permission without supplying an exact approved permission through the Python API; validation must return `policy_blocked`.
- Request rollback to a version not installed; rollback must fail without changing `active.json`.

## Boundaries

Confirm no workflow enables remote pack discovery, public marketplace behavior, in-process imports, untrusted execution, implicit permissions, credentials, provider promotion, recommendations, brokers, autonomous trading, or real-capital orders.

The example-specific guide is at `examples/runtime-packs/dry-run/README.md`.
