# Security Architecture Baseline

- **Status:** Draft for M0 acceptance
- **Scope:** Technology-neutral security obligations for OSCA

## Security objectives

OSCA must preserve confidentiality, integrity, availability, accountability, provenance, and least privilege across user actions, automation, providers, extensions, models, workflows, retained artifacts, and administrative operations.

Security controls must not silently weaken reproducibility or recovery. Security-relevant decisions and denials must be observable without exposing secrets or sensitive content.

## Trust boundaries

The architecture recognizes at least these boundaries:

1. user device and presentation surface;
2. authenticated OSCA application boundary;
3. capability-module boundaries with explicit ownership;
4. persistence and durable-artifact boundary;
5. provider and external-service boundary;
6. extension execution boundary;
7. model and LLM service boundary;
8. administrative and operational boundary;
9. backup, restore, and disaster-recovery boundary.

Crossing a boundary requires explicit identity, authorization, validation, protected transport, audit context, and failure handling appropriate to the risk.

## Identity and authentication

- Human, service, workflow, extension, provider, and administrative identities are distinct identity classes.
- Shared identities are prohibited for accountable operations.
- Service-to-service communication must use mutually authenticated secure channels where a network boundary exists.
- Authentication material must be short-lived where practical, rotatable, revocable, and never embedded in source or retained research artifacts.
- Recovery procedures must include restoration of trust relationships without restoring expired or compromised credentials.

## Authorization

- Authorization is deny-by-default and evaluated at capability entry points.
- Permissions are based on explicit subject, action, resource, scope, and contextual constraints.
- Internal module location does not imply authorization.
- Administrative operations, extension installation, credential access, model promotion, data export, workflow impersonation, and destructive recovery actions require elevated authority.
- Authorization checks and policy versions must be testable and auditable.

## Secure communications

All network transfers carrying credentials, user data, market data, artifacts, model inputs, workflow state, or control commands must use current secure transport with server authentication. Client authentication is mandatory for privileged service-to-service and administrative channels unless an approved equivalent control exists.

Certificate and trust-anchor lifecycle, rotation, revocation, hostname or service identity verification, downgrade prevention, and failure behavior must be documented and tested.

## Secrets

- Secrets are referenced, not copied into configuration, logs, artifacts, prompts, datasets, or extension packages.
- Access is least-privilege, purpose-bound, auditable, and revocable.
- Secret values must be redacted before telemetry leaves the owning boundary.
- Rotation must avoid unnecessary downtime and include rollback and compromise procedures.

## Data protection

- Data classification and ownership are mandatory before durable storage or external transfer.
- Sensitive data is minimized, encrypted in transit, and protected at rest according to classification.
- Exports, backups, caches, logs, prompts, and temporary files inherit the source classification.
- Retention and deletion must be explicit, verifiable, and compatible with legal holds and reproducibility commitments.

## Extensions and supply chain

- Extensions declare identity, publisher, version, permissions, capabilities, dependencies, compatibility ranges, and integrity metadata.
- Installation and activation are separate authorized actions.
- Untrusted extension content cannot obtain implicit access to internal packages, persistence, credentials, network, filesystem, models, or user data.
- Dependencies and build inputs require provenance, integrity verification, vulnerability scanning, and reproducible or attestable build evidence where feasible.

The exact extension isolation mechanism remains a later ADR.

## LLM and model security

- LLM outputs and model predictions are untrusted inputs until validated.
- Tool access is allow-listed, scoped, budgeted, authorized, and recorded.
- Sensitive context is minimized and provider transfer is policy-controlled.
- Prompt injection, data exfiltration, unsafe tool arguments, model substitution, and provenance loss are explicit threat cases.
- Models and prompts used for consequential outputs are versioned and attributable.

## Audit and observability

Security telemetry must record actor, action, target, decision, policy or contract version, correlation, outcome, and relevant provenance without recording secrets.

Audit records are append-protected, time-consistent, queryable, retention-governed, and included in backup and recovery validation.

## Threat-model lifecycle

Each capability and public seam must identify assets, actors, entry points, trust crossings, abuse cases, mitigations, residual risk, and verification evidence. Threat-model deltas are mandatory for security-sensitive changes under ADR-0005.

## Security failure principles

- Fail closed for authorization, identity, integrity, and trust verification.
- Do not convert validation failures into permissive defaults.
- Preserve enough evidence for diagnosis without leaking protected data.
- Support isolation, revocation, rollback, and recovery.
- Treat repeated partial failures as an operational security signal.
