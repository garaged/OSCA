# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P11 deterministic local analyst path:** Complete
- **P12 optional model-assisted preview:** Complete through PR #55
- **P13 governed production ingestion:** Complete through PR #56
- **Current activity:** P14 personal-server operations candidate in PR #57
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## P14 operations boundary

P14 adds `osca.personal_server` as an explicit operator-controlled runtime for a trusted single-user host.

- **Exposure:** loopback is the default; non-loopback configuration requires TLS and authentication.
- **Scheduler:** only locally configured and explicitly enabled commands execute, with bounded timeouts and retained stdout/stderr evidence.
- **Alerts:** file and HTTPS webhook transports are supported; delivery is disabled by default and webhook destinations are redacted.
- **Backup:** selected state is archived to a filesystem destination outside the source tree with manifest, file count, and SHA-256 evidence.
- **Restore:** archives are validated and extracted to temporary staging before copy; non-empty destinations require explicit overwrite permission.
- **Packaging:** systemd service and timer templates include common least-privilege hardening directives.

## Operator-owned controls

P14 does not provision certificates, identities, firewall policy, host patching, storage mounts, filesystem ownership, or cloud infrastructure. Operators must adapt and validate these controls for their host.

## Preserved boundaries

P14 does not enable multi-tenant SaaS, anonymous public access, remote arbitrary command submission, provider scope expansion, recommendations, brokers, autonomous execution, or real-capital orders.

## Authoritative navigation

- [P14 milestone](docs/milestones/p14/README.md)
- [P14 quickstart](docs/milestones/p14/user-testing-quickstart.md)
- [P13-P14 reconciliation](docs/governance/p13-p14-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Validation state

P13 is complete with final Quality run `30647766605` and merge commit `b22d23970be25f6425c4e5bd4d8a8ea51bb38335`. P14 remains an implementation candidate until PR #57 passes final hosted Quality, review, and evidence reconciliation.
