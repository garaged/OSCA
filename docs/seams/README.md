# OSCA Public Seams

- **Status:** Draft
- **Governing role:** Architecture authority
- **Purpose:** Define technology-neutral public capability boundaries used by clients, modules, extensions, retained workflows, and external integrations.
- **Authoritative sources:** PRD sections 12, 15–16, 20–25, 29–30; ADR-0002; ADR-0003; architecture principles and dependency rules
- **Downstream consumers:** Module catalog, repository structure, API and schema design, extension SDKs, contract tests, compatibility policy, and implementation specifications

## Common seam obligations

Every public seam must define:

- owning capability and non-responsibilities;
- typed commands, queries, events, or execution contracts;
- stable identities and temporal semantics;
- validation, permissions, provenance, and audit behavior;
- failure categories, retryability, idempotency, and partial-result behavior;
- determinism, random-seed, quality, and freshness semantics where applicable;
- resource budgets and cancellation behavior;
- compatibility scope and conformance fixtures;
- observability and diagnostics;
- documentation and examples.

Public seams are narrower and more stable than ordinary internal module interfaces. They must not expose persistence entities, provider SDK types, framework objects, internal file paths, or arbitrary database-shaped records.

## Seam specifications

- [Provider seam](provider-seam.md)
- [Analysis seam](analysis-seam.md)
- [Visualization seam](visualization-seam.md)
- [Model seam](model-seam.md)
- [LLM seam](llm-seam.md)
- [Extension seam](extension-seam.md)
- [Workflow seam](workflow-seam.md)

## Current decision boundary

The seam responsibilities and mandatory metadata are defined here. Their durable compatibility and version-selection rules require a common public-contract versioning decision before these specifications can be accepted.