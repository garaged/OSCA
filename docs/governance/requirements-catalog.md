# Requirements Catalog

- **Status:** Active baseline catalog
- **Governing role:** Product authority
- **Purpose:** Assign stable identifiers and engineering metadata to testable requirements derived without semantic change from the approved PRD and active decisions.
- **Authoritative sources:** [Product requirements](../product-requirements.md), [decision log](../decision-log.md), [ADR-0001](../decisions/ADR-0001-requirements-authority-and-traceability-model.md)
- **Downstream consumers:** Milestone intents, specifications, acceptance criteria, tests, documentation, risk treatments, and automated traceability checks

## Authority

This catalog is an index and decomposition of authoritative requirements. It does not replace the PRD or active accepted decisions and cannot change their meaning.

If a catalog entry conflicts with its cited source, the cited source governs and the catalog entry must be corrected. A proposed correction that changes product meaning requires product decision governance.

## Identifier policy

Requirements receive immutable identifiers in the form `REQ-NNNN`.

The numeric identifier carries no domain or milestone meaning. Classification and allocation are stored as metadata so a requirement can move between modules or milestones without changing identity.

Identifiers are never reused. A retired or superseded requirement remains in the catalog with its history and replacement reference.

## Required fields

Each catalog entry must contain:

| Field | Meaning |
|---|---|
| ID | Stable `REQ-NNNN` identifier |
| Title | Short unique description |
| Normative statement | Atomic, testable requirement using defined requirement language |
| Authority | Exact PRD section and applicable decision IDs |
| Classification | Product behavior, architecture constraint, quality attribute, security, process, documentation, or governance |
| Scope | Affected capability or cross-cutting concern |
| Planned milestones | Milestones expected to specify or satisfy the requirement |
| Verification class | Test, analysis, inspection, demonstration, or mixed |
| Risk links | Related risk identifiers |
| Status | Active, superseded, retired, or deferred |
| Supersedes / superseded by | Requirement-history links |
| Notes | Non-normative clarification only |

## Decomposition rules

- Each normative statement expresses one independently verifiable obligation where practical.
- Decomposition may make implicit subjects or conditions explicit but cannot add behavior.
- Requirement language follows the approved PRD definitions.
- A requirement may cite multiple PRD passages and decisions.
- A PRD passage may produce multiple catalog requirements when it contains separable obligations.
- Duplicate requirements are consolidated while preserving all authority links.
- Implementation details are excluded unless already mandated by an authoritative source.
- Unresolved design questions are not converted into requirements.

## Population status

The catalog policy is accepted. Exact numbered requirements are extracted and reviewed when a milestone selects their scope, keeping decomposition small and reviewable. ADR-0001 requires the selected entries and machine-validatable links before implementation depends on them.

## Catalog entries

The following entries are proposed for M1 product-authority review. They become Active only when the M1 intent is accepted.

| ID | Title | Normative statement | Authority | Classification | Scope | Milestone | Verification | Risk links | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-0001 | Runnable local product | OSCA must run locally as one coherent minimal product using the single-user modular-monolith topology. | PRD M1; D-006; D-007 | Product behavior | Cross-cutting | M1 | Demonstration, test | Architecture drift | Draft |
| REQ-0002 | Shared application behavior | Web, API, and CLI clients must invoke shared application capabilities and must not duplicate authoritative business or security rules. | PRD 16.2, 16.6; D-021 | Architecture constraint | Interfaces | M1 | Structural, contract | Interface divergence | Draft |
| REQ-0003 | Web readiness shell | The web shell must expose the M1 system-readiness outcome as OSCA's primary interactive surface. | PRD 16.1; PRD M1 | Product behavior | Web adapter | M1 | End-to-end, accessibility | User effectiveness | Draft |
| REQ-0004 | Versioned readiness API | OSCA must expose the readiness capability through an explicitly versioned application API with structured validation and errors. | PRD 16.2, 16.6; PRD M1 | Product behavior | API adapter | M1 | Contract, end-to-end | Compatibility | Draft |
| REQ-0005 | Readiness CLI | OSCA must expose readiness, diagnostic-job, configuration, backup, and restore operations through the CLI where included in M1 scope. | PRD 16.3; PRD M1 | Product behavior | CLI adapter | M1 | Contract, end-to-end | Automation reliability | Draft |
| REQ-0006 | Loopback-safe local profile | Local-only mode must bind to loopback or a protected local channel by default and rely on the operating-system user boundary. | PRD 26.1; D-031 | Security | Security/configuration | M1 | Security-negative, integration | Unsafe exposure | Draft |
| REQ-0007 | Explicit network exposure | Binding to a non-local interface must require explicit configuration, and unsafe remote exposure must be rejected where practical. | PRD 26.1; D-031 | Security | Security/configuration | M1 | Security-negative | Unsafe exposure | Draft |
| REQ-0008 | Protected remote profile | The personal-server configuration skeleton must require authenticated sessions and authenticated encrypted transport for protected remote operations. | PRD 26.1, 26.3; D-031; D-032 | Security | Security/transport | M1 | Analysis, security-negative | Identity and transport compromise | Draft |
| REQ-0009 | Vault-backed secret abstraction | Credentials must use an operating-system credential store or replaceable encrypted secret-vault adapter, and consumers must use named secret references rather than secret values. | PRD 26.2; D-031 | Security | Secrets | M1 | Component, security-negative | Secret disclosure | Draft |
| REQ-0010 | Secret exclusion | Secrets must not appear in logs, errors, URLs, manifests, ordinary backups, exported configuration, or diagnostic bundles. | PRD 26.2, 28.4 | Security | Cross-cutting | M1 | Security-negative, inspection | Secret disclosure | Draft |
| REQ-0011 | Durable job identity | Every M1 diagnostic job and run must have a stable typed identity and expose durable status and progress. | PRD 16.2, 29.2; D-036 | Product behavior | Workflow | M1 | Component, contract | Lost or ambiguous work | Draft |
| REQ-0012 | Durable job lifecycle | The diagnostic job must define inputs, outputs, idempotency, concurrency, checkpoint, retry, cancellation, safe shutdown, and restart/resume behavior. | PRD 29.2, 29.3; D-036 | Quality attribute | Workflow | M1 | Component, failure, recovery | Workflow corruption | Draft |
| REQ-0013 | Typed metadata identity | Retained M1 job, configuration, and backup records must have stable typed identity, schema/revision, timestamps, producer/build identity, lineage, integrity, and availability metadata as applicable. | PRD 11, 13.5; PRD M1 | Product behavior | Catalog | M1 | Schema, component | Provenance loss | Draft |
| REQ-0014 | Structured correlated telemetry | M1 behavior must emit structured logs, metrics, traces, job events, and distinct audit records connected by correlation identities. | PRD 28.2, 28.4; D-035 | Quality attribute | Operations | M1 | Component, observability | Undiagnosable failure | Draft |
| REQ-0015 | Built-in health | The built-in readiness experience must distinguish healthy, degraded, blocked, recovering, and unavailable states and provide impact and remediation guidance. | PRD 28.1; D-035 | Product behavior | Operations | M1 | Component, end-to-end | Silent failure | Draft |
| REQ-0016 | Configuration validation | OSCA must validate configuration before serving or running affected work and return actionable structured diagnostics for invalid or unsafe combinations. | PRD M1; PRD 26.1, 26.3 | Security | Configuration | M1 | Unit, property, security-negative | Misconfiguration | Draft |
| REQ-0017 | Minimal protected backup | M1 must create a consistent minimal backup containing required configuration references, metadata, job state, manifests, and audit metadata while excluding secrets and transient content. | PRD 27.1, 27.2; PRD M1 | Product behavior | Recovery | M1 | Component, integration | State loss, secret disclosure | Draft |
| REQ-0018 | Verified isolated restore | M1 restore must verify integrity and compatibility, preview impact, restore into an isolated location, and leave active state unchanged until validation succeeds. | PRD 27.3, 27.5; PRD M1 | Product behavior | Recovery | M1 | Recovery, security-negative | Corrupt or unsafe restore | Draft |
| REQ-0019 | Version-matched executable documentation | M1 installation, configuration, security, interface, job, backup/restore, and troubleshooting documentation must match the product version, and executable examples must be automatically validated where practical. | PRD 17; D-022; PRD M1 | Documentation | Cross-cutting | M1 | Inspection, executable example | Documentation drift | Draft |
| REQ-0020 | Evidence-based completion | M1 behavior is complete only when requirements, specifications, acceptance criteria, implementation, verification, documentation, observability, failure behavior, and residual risks are traceably evidenced. | PRD 38; universal milestone exit gate; D-042; D-046 | Governance | Cross-cutting | M1 | Traceability audit | False completion | Draft |

Detailed supersession fields and notes are empty for these initial entries. No identifier may be reused if an entry is rejected or retired.
