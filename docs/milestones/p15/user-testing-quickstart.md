# P15 User Testing Quickstart

Use only disposable local packs you trust. P15 is not a hostile-code sandbox.

## Prepare a sample pack

```bash
rm -rf .osca/p15-manual /tmp/osca-example-pack
mkdir -p /tmp/osca-example-pack
cat >/tmp/osca-example-pack/run.py <<'PY'
#!/usr/bin/env python3
import json
import sys
payload = json.load(sys.stdin)
print(json.dumps({"pack": "example-analysis", "received": payload}))
PY
chmod 700 /tmp/osca-example-pack/run.py
DIGEST="sha256:$(shasum -a 256 /tmp/osca-example-pack/run.py | awk '{print $1}')"
cat >/tmp/osca-example-pack/osca-pack.json <<JSON
{
  "package_id": "example-analysis",
  "package_version": "1.0.0",
  "publisher": "local-operator",
  "category": "analysis",
  "executable": "run.py",
  "osca_min_version": "0.1.0",
  "trust_tier": "local_trusted",
  "integrity_digest": "$DIGEST",
  "permissions": [],
  "max_runtime_seconds": 10,
  "max_output_bytes": 10000
}
JSON
```

## Validate

```bash
uv run python -m osca.runtime_extensions validate /tmp/osca-example-pack \
  --storage-root .osca/p15-manual
```

Expected: `validated`, exact package/version and digest, no process execution.

## Confirm execution is disabled by default

```bash
uv run python -m osca.runtime_extensions run /tmp/osca-example-pack \
  --storage-root .osca/p15-manual \
  --input '{"symbol":"AAPL"}'
```

Expected: `policy_blocked` and `execution-disabled`.

## Execute explicitly

```bash
uv run python -m osca.runtime_extensions run /tmp/osca-example-pack \
  --storage-root .osca/p15-manual \
  --input '{"symbol":"AAPL"}' \
  --enable
```

Expected: `succeeded`, exit code `0`, retained stdout/stderr URIs, and output digest under `.osca/p15-manual/runtime-extensions/example-analysis/evidence/`.

## Install

```bash
uv run python -m osca.runtime_extensions install /tmp/osca-example-pack \
  --storage-root .osca/p15-manual
```

Expected: `installed`, versioned package directory, and `active.json` pointer.

## Negative checks

- Change one byte in `run.py`; validation must fail with digest mismatch.
- Change `trust_tier` to `untrusted`; validation must return `policy_blocked`.
- Change `osca_min_version` to `9.0.0`; validation must return `incompatible`.
- Add a manifest permission without supplying an exact approved permission through the Python API; validation must return `policy_blocked`.
- Request rollback to a version not installed; rollback must fail without changing `active.json`.

## Boundaries

Confirm no workflow enables remote pack discovery, public marketplace behavior, in-process imports, untrusted execution, implicit permissions, credentials, provider promotion, recommendations, brokers, autonomous trading, or real-capital orders.
