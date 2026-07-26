# P14 - Production Operations

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Make personal-server operation credible with scheduler execution, external alerts, backup transport, restore execution, release packaging, and security hardening.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p14-production-operations.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p14-production-operations/spec.md)

## Objective

Make personal-server operation credible with scheduler execution, external alerts, backup transport, restore execution, release packaging, and security hardening.

## User-visible value

A user can operate OSCA as a durable local/personal service rather than a demo script.

## Implementation scope

- Implement scheduler execution for governed jobs.
- Implement external alert delivery where configured.
- Implement off-device backup transport and active restore execution.
- Harden TLS/session/auth configuration and release packaging.

## Explicit non-scope

- Multi-tenant SaaS, real-money execution.

## Acceptance criteria

- REQ-0254-REQ-0260 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P10-P13 and M12 contracts.

## Risks and decisions

Security review is required before exposing personal-server surfaces.
