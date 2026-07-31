# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P11 deterministic local analyst path:** Complete
- **P12 optional model-assisted preview:** Complete through PR #55
- **P13 governed production ingestion:** Complete through PR #56
- **P14 personal-server operations:** Complete through PR #57
- **Current activity:** P15 governed runtime extension packs candidate in PR #58
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## P15 extension boundary

P15 adds `osca.runtime_extensions` as a trusted-local runtime built on the accepted M5 extension contracts.

- **Trust:** only built-in, verified, or independently accepted local-trusted packs may execute.
- **Integrity:** the manifest SHA-256 must match the direct pack executable.
- **Compatibility:** the pack's declared OSCA minimum version must be satisfied.
- **Permissions:** approved permissions must exactly match the manifest; any change requires renewed approval.
- **Execution:** explicit enablement, direct subprocess without a shell, minimized environment, bounded runtime/output, and JSON-object output validation.
- **Evidence:** package/version, digest, permissions, stdout/stderr, output digest, exit code, rationale, and findings are retained.
- **Lifecycle:** validated versions install into explicit package/version paths and rollback targets only an already installed revalidated version.

## Security interpretation

The direct subprocess boundary reduces in-process blast radius but is not a complete hostile-code sandbox. P15 does not authorize untrusted or quarantined code execution. Broader isolation using containers, VMs, seccomp, or mandatory-access-control profiles requires a separate architecture and security decision.

## Preserved boundaries

P15 does not enable public marketplaces, remote pack discovery, in-process arbitrary imports, implicit permission renewal, provider admission expansion, credentials, recommendations, brokers, autonomous execution, or real-capital orders.

## Authoritative navigation

- [P15 milestone](docs/milestones/p15/README.md)
- [P15 quickstart](docs/milestones/p15/user-testing-quickstart.md)
- [P14-P15 reconciliation](docs/governance/p14-p15-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Validation state

P14 is complete with final Quality run `30650397785` and merge commit `3aa884b4894e4f956fa93e1d70cf1930329b83b4`. P15 remains an implementation candidate until PR #58 passes final hosted Quality, review, and evidence reconciliation.
