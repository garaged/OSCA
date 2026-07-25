# M5.3 Extension CLI Administration Evidence

- **Milestone:** M5 independent extension packaging and activation
- **Slice:** M5.3 metadata-only CLI administration
- **Branch:** `agent/m5-extension-packaging`
- **Head:** `71afb66bc6be86c7d3e9bb3c4a0445ae38cb64af`
- **Hosted Quality run:** `30151415441`
- **Status:** Passed
- **Recorded:** 2026-07-25

## Scope evidenced

- `extension-install` creates and persists installation records from valid manifests.
- `extension-activate` records explicit activation decisions for stored installations.
- `extension-list` lists persisted installation records from the lifecycle store.
- Unknown installation activation fails with an operator-visible error.
- CLI tests verify metadata-only administration without runtime extension execution.

## Hosted gates

- OpenSpec doctor: passed.
- Strict OpenSpec validation: passed.
- Secret scan: passed.
- Ruff: passed.
- Strict mypy: passed.
- Pytest: passed.
- Contracts, migrations, documentation links, and architecture validation: passed.

## Residual scope

Runtime loading/execution, HTTP API/UI administration, public registry behavior, strategy/backtesting, ML, LLM, paper trading, and live execution remain deferred.
