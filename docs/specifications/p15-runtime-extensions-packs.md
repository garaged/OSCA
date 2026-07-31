# P15 Runtime Extensions and Packs Specification

## Purpose

Allow trusted local provider, analysis, and visualization packs to execute through governed extension lifecycle controls without modifying the OSCA core repository.

## Phase

Production-capable version

## User-visible value

A local operator can validate, install, execute, inspect, and roll back a trusted extension pack while preserving exact version, integrity, permission, compatibility, and execution evidence.

## Requirements

- **REQ-0261:** P15 must provide a trusted local runtime extension path built on the accepted M5 extension contracts.
- **REQ-0262:** Runtime packs must declare exact identity, semantic version, publisher, category, executable, compatibility floor, trust tier, SHA-256 digest, permissions, determinism, timeout, and output budget.
- **REQ-0263:** Validation must fail closed for untrusted or quarantined packs, digest mismatch, incompatible OSCA versions, undeclared or unapproved permission changes, invalid executable paths, or malformed manifests.
- **REQ-0264:** Execution must require explicit operator enablement and use a direct subprocess with no shell, bounded runtime/output, minimized environment, and structured JSON-object output.
- **REQ-0265:** Successful and failed executions must retain immutable evidence including package/version, digest, permission approvals, stdout/stderr locations, output digest, exit code, rationale, and findings.
- **REQ-0266:** Installation and rollback must operate only on validated local versions; rollback must target an already installed version and update an explicit active-version pointer.
- **REQ-0267:** P15 completion requires conformance tests, manual usage, OpenSpec, traceability, architecture status, exit review, secret scanning, and hosted Quality evidence.

## Implementation scope

- Reuse M5 extension trust tiers, permissions, categories, and lifecycle concepts.
- Validate external pack directories containing `osca-pack.json` and one direct executable.
- Install trusted pack versions under the configured OSCA storage root.
- Execute explicitly enabled packs as bounded subprocesses.
- Retain execution evidence and support rollback to an installed version.
- Provide CLI commands for validation, installation, execution, and rollback.
- Add external-pack conformance tests.

## Explicit non-scope

- Public marketplace or remote pack discovery.
- Untrusted or quarantined arbitrary code execution.
- In-process dynamic imports into the OSCA process.
- OS-level container, VM, seccomp, or mandatory-access-control sandbox provisioning.
- Automatic permission renewal or implicit grants.
- Provider admission expansion, credential materialization, recommendations, broker connections, autonomous trading, or real-capital orders.

## Security and architecture decision

P15 deliberately chooses **trusted local subprocess isolation** rather than broad untrusted-code sandboxing. A direct subprocess boundary reduces in-process blast radius, but it is not a complete hostile-code sandbox. Only packs the local operator has independently trusted may execute. Broader untrusted execution requires a separate architecture and security decision.

## Acceptance criteria

- Trusted compatible packs with exact digests and exact permission approval validate.
- Untrusted, incompatible, tampered, or permission-mismatched packs fail closed before execution.
- Execution is disabled by default and uses no shell.
- Runtime and output budgets are enforced.
- Pack output must be a JSON object.
- Evidence is retained for success and failure.
- Rollback succeeds only to a previously installed validated version.
- P14 safety and production-operation boundaries remain unchanged.

## Dependencies

M5 and P11-P14.
