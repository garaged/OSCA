# P15 - Runtime Extensions and Packs

- **Status:** Implementation candidate in PR #58
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Allow trusted local provider, analysis, and visualization packs to execute through governed lifecycle controls without modifying OSCA core.
- **Baseline:** P14 merge commit `3aa884b4894e4f956fa93e1d70cf1930329b83b4`
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality pending

## Objective

Provide a fail-closed trusted-local extension runtime with exact integrity, compatibility, permission, resource, evidence, and rollback controls.

## User-visible value

A local operator can validate, install, execute, inspect, and roll back an external pack while retaining reproducible evidence.

## Implementation scope

- Reuse accepted M5 trust-tier, permission, category, and lifecycle contracts.
- Validate `osca-pack.json`, direct executable path, semantic versions, OSCA compatibility, exact executable SHA-256, and exact permission approval.
- Install pack versions under `<storage-root>/runtime-extensions/<package>/<version>`.
- Execute only explicitly enabled trusted packs through a direct subprocess with no shell.
- Enforce timeout and output-size budgets plus JSON-object output.
- Retain stdout, stderr, output digest, exit code, version identity, permissions, rationale, and findings.
- Roll back only to a previously installed and revalidated version.
- Expose validate, install, run, and rollback CLI commands.

## Explicit non-scope

- Public marketplace or remote discovery.
- Untrusted or quarantined execution.
- In-process arbitrary imports.
- Complete hostile-code sandboxing.
- Implicit permission grants or renewal.
- Provider admission expansion, credentials, recommendations, brokers, autonomous trading, or real-capital orders.

## Acceptance criteria

- REQ-0261 through REQ-0267 map to code, tests, documentation, and exit evidence.
- Untrusted, incompatible, tampered, or permission-mismatched packs fail before process start.
- Execution is disabled by default.
- Successful execution retains structured evidence.
- Rollback changes only the explicit active-version pointer and only to an installed version.
- P14 production-operation and security boundaries remain intact.
- Hosted Quality passes before P15 is marked complete.

## Current artifacts

- [Specification](../../specifications/p15-runtime-extensions-packs.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p15-runtime-extensions-packs/spec.md)
- [User testing quickstart](user-testing-quickstart.md)
- [Exit review](exit-review.md)
- [P14-P15 reconciliation](../../governance/p14-p15-reconciliation.md)
