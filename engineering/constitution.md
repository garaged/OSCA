# OSCA Engineering Constitution

## Purpose

This constitution distills the stable rules that govern human and AI-assisted delivery. Detailed authority remains in accepted requirements, ADRs, specifications, and quality policies.

## Architecture compass

When artifacts conflict, resolve them in this order:

1. Accepted user intent and product requirements
2. Accepted foundational ADRs
3. Quality attributes and security obligations
4. Approved specifications
5. Reference capability guidance
6. Implementation choices

Lower-level artifacts must not silently weaken higher-level authority.

## Constitutional invariants

1. Work starts from an explicit intent.
2. Requirements define observable behavior and are never inferred from implementation alone.
3. Consequential decisions are recorded before implementation commits the project to them.
4. Capabilities own their domain behavior and persistent state.
5. Public contracts are intentional, owned, versioned, and compatibility governed.
6. Cross-capability communication semantics are explicit.
7. Extensions use public seams and receive least privilege.
8. Security defaults to deny and sensitive transfers use authenticated secure channels.
9. Observability is part of feature completion.
10. Recovery is designed, exercised, and evidenced.
11. Verification strength is proportional to change risk.
12. Documentation, migration, traceability, and operational evidence are deliverables.

## Engineering loop

```text
Intent
  -> Requirements
  -> Architecture
  -> Specification
  -> Implementation
  -> Verification
  -> Evidence
  -> Operational review
  -> Lessons learned
```

Lessons learned inform future work. They do not amend frozen architecture implicitly.

## Golden review questions

Every change must identify:

- the intent and requirements it serves;
- the owning capability and affected contracts;
- applicable ADRs and quality attributes;
- interaction type: query, command, event, or workflow;
- state ownership and migration impact;
- security, extension, recovery, and compatibility impact;
- telemetry and audit behavior;
- verification evidence and documentation changes.

## Completion rule

A change is complete only when implementation, verification, documentation, traceability, compatibility, security, observability, and recovery obligations appropriate to its risk have been satisfied or covered by an approved, expiring exception.
