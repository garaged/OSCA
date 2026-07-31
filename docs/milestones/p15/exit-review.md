# P15 Exit Review

- **Milestone:** P15 governed runtime extension packs
- **Status:** Implementation candidate; final hosted Quality and review pending
- **Branch:** `agent/p15-governed-runtime-extension-packs`
- **Pull request:** #58
- **Baseline:** merged P14 commit `3aa884b4894e4f956fa93e1d70cf1930329b83b4`

## Implemented evidence

- Trusted local pack manifest, request, execution evidence, and rollback evidence contracts.
- Exact executable SHA-256 verification.
- OSCA compatibility and M5 trust-tier validation.
- Exact permission-set approval.
- Direct subprocess execution without shell invocation.
- Minimized environment with explicit network and secret disabled markers.
- Runtime and output-size budgets.
- JSON-object output validation.
- Retained stdout, stderr, output digest, exit code, package/version, rationale, and findings.
- Versioned installation plus rollback to an already installed revalidated version.
- CLI and manual quickstart.

## Safety behavior

- Execution is disabled by default.
- Untrusted and quarantined packs are blocked.
- Tampered and incompatible packs fail before execution.
- Pack executables must be direct regular files inside the pack directory.
- Public marketplace, remote discovery, in-process arbitrary imports, broad hostile-code sandboxing, and implicit permission renewal remain deferred.
- Provider admission, credentials, recommendations, brokers, autonomous trading, and real-capital orders remain unchanged and disabled where previously deferred.

## Automated validation

Eight focused tests cover trusted validation, untrusted blocking, compatibility blocking, digest tampering, disabled execution, successful execution evidence, versioned installation and rollback, and missing rollback versions.

## Hosted validation

Pending final review-ready run:

- Ruff
- strict mypy
- pytest, contracts, migrations, links, and architecture checks
- OpenSpec doctor and strict validation
- secret scanning

## Completion decision

P15 remains an implementation candidate until final hosted Quality is green, documentation and traceability are reconciled, the branch diff is reviewed, and PR #58 is merged.
