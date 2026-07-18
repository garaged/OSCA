# M1.7 documentation and operational evidence

- **Status:** Complete
- **Validated source checkpoint:** `5906e0e5c47d5f2640fa8e8eabb075ea177fec6c`
- **Branch:** `agent/m1-documentation-operational-evidence`
- **GitHub Actions run:** `29653058721`
- **Requirements:** REQ-0019, REQ-0020
- **Acceptance criteria:** M1-AC-001, M1-AC-003, M1-AC-018, M1-AC-020
- **Decisions:** ADR-0001, ADR-0004, ADR-0005, ADR-0009, ADR-0010
- **OpenSpec change:** `m1-7-documentation-operational-evidence`
- **Validated:** 2026-07-18

## Delivered result

- Repository-backed gap analysis recorded before implementation.
- One version-matched, non-normative run-and-operate path from clean setup through readiness, diagnostic work, recovery, telemetry, troubleshooting, contracts, and limitations.
- Existing diagnostic and recovery guidance retained as focused sources rather than duplicated.
- Root, M1, evidence-plan, recovery-status, and REQ-0019/REQ-0020 navigation reconciled.
- Executable-example matrix distinguishes CI-executed behavior from platform-, identity-, and operator-specific procedures.

## Retained validation

GitHub Actions run `29653058721` passed against the validated source checkpoint:

| Gate | Result |
|---|---|
| Locked Python 3.13 environment | Pass |
| Ruff | Pass |
| Strict mypy | Pass |
| Tests, contracts, migrations, documentation links, and architecture | Pass |
| OpenSpec doctor and strict validation | Pass |
| Secret scan | Pass |

The test suite exercises the shared readiness behavior, CLI/API/web contracts, durable diagnostics, recovery interoperability and negative paths, migrations, schema determinism, architecture boundaries, and documentation links. The run is the immutable bulk-output identity; this record retains its governed summary.

## Documentation-example disposition

| Example family | Disposition |
|---|---|
| Locked setup and migrations | Executed by CI |
| CLI/API/web readiness | Exercised by contract/end-to-end tests; documented loopback commands are version matched |
| Diagnostic lifecycle | Exercised by CLI, component, lifecycle, restart/resume, and cancellation tests |
| Backup and isolated restore | Exercised with pinned age interoperability and recovery/security-negative tests |
| Real credential identity custody | Operator- and platform-specific; adapter behavior is tested and no secret example is retained |
| Personal-server deployment | Fail-closed configuration behavior is tested; production deployment certification is deferred |

## Traceability conclusion

REQ-0019 is satisfied for M1 by the version-matched guide, focused capability pages, executable-example disposition, and passing documentation/product gates. REQ-0020 is satisfied for the M1.7 slice by links from requirement authority through specification, acceptance criteria, documentation, validation, and this evidence record. M1 milestone acceptance remains pending M1.8.

## Residual risks and limitations

- Credential-store and dual-stack behavior remain platform-dependent and require target-platform conformance evidence before a supported-platform claim.
- Personal-server configuration is a protected validation skeleton, not public-internet hardening certification.
- Production recovery requires a compatible external age executable and separately custodied identity.
- Documentation commands that require real credentials or operator-owned destinations cannot safely be copied into deterministic CI with production material.
- This record validates M1.7, not the M1.8 exit review.

## Integrity and exceptions

No exception is open. The exact source checkpoint and immutable Actions run identify the validated material; the final archival/navigation commit is subject to the same required PR checks before merge.
