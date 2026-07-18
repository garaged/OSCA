# M1 Scope — Secure Walking Skeleton

- **Status:** Proposed
- **Governing role:** Product authority
- **Architecture approval:** Architecture authority
- **Authoritative sources:** M1 intent; approved PRD M1 outcome; Tier-1 ADRs
- **Last reviewed:** 2026-07-18

## Vertical-slice boundary

M1 is organized around **system readiness**, not around separate infrastructure layers.

A single readiness request traverses a presentation adapter, versioned application contract, configuration/security policy, health aggregation, metadata identity, telemetry, and persistence. A related diagnostic job proves durable execution. Backup/restore proves recovery of the minimal state introduced by the slice.

## Capability allocation

| Capability | M1 responsibility | State owned |
|---|---|---|
| Platform/Configuration | Resolve profiles and reject unsafe or invalid configuration | Validated configuration snapshot |
| Identity/Security | Establish local-owner context and secret references | Security profile and credential references |
| Workflow | Run and recover the diagnostic job | Job identity, lifecycle, checkpoint, result reference |
| Catalog | Record typed metadata for retained M1 artifacts | Metadata identity, revision, lineage, availability |
| Operations | Aggregate readiness and structured diagnostics | Health observations and operational findings |
| Recovery | Create, verify, preview, and restore minimal backups | Backup manifest and restore record |
| Interface adapters | Render/invoke shared capabilities | No authoritative product state |

Names are logical capability labels pending the physical module-layout decision. This table does not create shared mutable ownership.

## Required end-to-end scenarios

1. Start a valid local profile and inspect readiness from web, API, and CLI.
2. Reject unsafe binding or inconsistent remote-security configuration before accepting traffic.
3. Store and resolve a named test secret through the vault abstraction without exposing its value.
4. Submit a diagnostic job, observe progress, interrupt the process, resume safely, and inspect the retained result.
5. Create a minimal backup, verify integrity, preview restore, restore into isolated storage, and confirm active state was not mutated.
6. Produce correlated diagnostic evidence and a distinct security-sensitive audit event.
7. Execute documented setup and example commands in automation.

## Deferred boundary

Concrete runtime, build system, repository syntax, persistence engine, workflow implementation, secret-vault adapter, API protocol/framework, web technology, telemetry SDK, and backup format require explicit M1 decisions or specifications. No prototype establishes a default.
