# Deferred Architecture Decisions

- **Status:** Active
- **Purpose:** Prevent intentional deferral from becoming an undocumented default

| ID | Decision | Why deferred | Required evidence or trigger | Decision authority |
|---|---|---|---|---|
| DD-001 | Programming language and primary runtime | Resolved for initial implementation by ADR-0011 | CPython 3.13 | Architecture authority |
| DD-002 | Build system and repository layout syntax | Resolved for initial implementation by ADR-0011 | uv, one Python distribution, src-layout, architecture tests | Architecture authority |
| DD-003 | Persistence technology | Resolved for M1 metadata by ADR-0012; market payload storage remains deferred | SQLite/SQLAlchemy/Alembic for M1 metadata only | Architecture authority and data owner |
| DD-004 | Inter-module communication model | Resolved by ADR-0006 | Accepted command, query, event, and workflow model | Architecture authority |
| DD-005 | Event reliability model | Resolved by ADR-0007; universal event sourcing was not selected | Accepted at-least-once, idempotent, replay-governed event model | Architecture authority and domain owners |
| DD-006 | Extension isolation model | Resolved by ADR-0008 | Accepted trust-tiered isolation model; concrete sandbox/runtime selection remains slice-dependent | Architecture and security authorities |
| DD-007 | UI framework | Presentation technology does not alter current domain governance | Target platforms, accessibility, visualization performance, packaging, team capability | Architecture and product authorities |
| DD-008 | ML framework and model-serving technology | Model contracts are more durable than framework choice | Initial model classes, reproducibility, hardware targets, packaging and isolation needs | ML capability owner and architecture authority |
| DD-009 | Workflow engine | Resolved for M1 by ADR-0013 | Embedded database-backed single-node executor | Workflow owner and architecture authority |
| DD-010 | Numeric RTO, RPO, availability, and performance budgets | Unsupported numbers would be fictional at M0 | Deployment topology, workload forecasts, business impact analysis, measured baselines | Product, operations, and architecture authorities |
| DD-011 | Serialization and API protocols | Resolved for M1 by ADR-0014; later streaming/binary needs remain trigger-bound | Pydantic, JSON Schema, OpenAPI 3.1, versioned JSON | Contract owners and architecture authority |
| DD-012 | Identity provider and cryptographic implementation | Resolved for the M1 local profile by ADR-0015 and M1 backup format by ADR-0016; future hosted identity remains deferred | OS credential store via keyring; fail-closed remote-profile skeleton; age v1 X25519 recovery container | Security authority |

## Disposition note

DD-004 through DD-006 are retained as historical identifiers and marked resolved. Concrete protocol, broker, workflow engine, sandbox, or runtime products remain governed by DD-001, DD-002, DD-009, DD-011, and relevant slice specifications.

## Rules

- A deferred decision must not be resolved implicitly by prototype code.
- Experiments may compare candidates but cannot establish an authoritative default without the required ADR or approved specification.
- Each decision is revisited when its trigger becomes true or before implementation would otherwise depend on it.
- New material alternatives, risks, and evidence are appended to the corresponding decision record.
