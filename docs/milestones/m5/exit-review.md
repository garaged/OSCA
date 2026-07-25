# M5 Exit Review

- **Milestone:** M5 independent extension packaging and activation
- **Status:** Accepted for PR review
- **Branch:** `agent/m5-extension-packaging`
- **Last reviewed:** 2026-07-25

## Scope accepted

M5 starts from the completed M4 research-project baseline and adds the governed metadata-only extension lifecycle foundation.

Accepted M5 scope includes:

- Extension manifest, permission, dependency, schema, trust-tier, resource, integrity, license, and provenance contracts.
- Fail-closed manifest validation.
- Installation records preserving exact package identity, version, source, digest, dependencies, permissions, activation state, and timestamps.
- Explicit activation decisions with trust-tier and permission-renewal checks.
- Disable and uninstall impact previews.
- SQLite lifecycle persistence for installation records and activation decisions.
- Metadata-only CLI administration for install, activate, and list workflows.
- Requirements, traceability, OpenSpec, documentation, and retained evidence for REQ-0069-REQ-0084.

## Deferred scope

The following remain outside M5 and require later governed milestone intents:

- Runtime loading or execution of third-party extension code.
- Public extension registry operation.
- HTTP API/UI administration.
- Strategy research and backtesting.
- Paper trading and live execution.
- ML lifecycle and LLM-assisted analysis.
- Provider production promotion for paid, authenticated, or license-sensitive use.

## Exit decision

M5 is complete for the accepted scope once the final archived-head hosted Quality run passes OpenSpec strict validation, secret scan, Ruff, strict mypy, pytest, contracts, migrations, documentation links, and architecture validation.
