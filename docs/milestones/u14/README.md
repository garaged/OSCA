# U14 — Contributor and Extension Readiness

- **Status:** Complete
- **Baseline:** U13 merged and tagged `v0.1.0rc1` at `f3706085eddd9825e4e1fa23c3b3b96f1c920c70`
- **Implementation PR:** #77

## Outcome

U14 establishes a reproducible contributor workflow and a strict trusted-local extension conformance boundary without creating a public marketplace, remote installer, automatic updater, or hostile-code sandbox.

## Contributor path

```bash
uv sync --locked
npm ci --ignore-scripts
uv run python scripts/contributor_check.py
```

The canonical command runs Ruff, strict mypy, tests and architecture checks, OpenSpec validation, and the offline example-extension conformance check.

## Extension path

```bash
uv run osca extension validate \
  --manifest examples/extensions/offline-mean/osca-extension.json
```

Validation is machine-readable, fail-closed, and non-importing. It verifies identity, API compatibility, capabilities, provenance, licensing, trust classification, contained artifact paths, and SHA-256 digests.

## Safety

Only independently reviewed trusted-local extensions may proceed to any existing execution mechanism. Validation does not authorize execution. Public untrusted distribution, remote installation, automatic updates, recommendations, live serving, broker connectivity, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled.
