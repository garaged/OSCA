# Deferred Architecture Decisions

- **Status:** Active
- **Purpose:** Prevent intentional deferral from becoming an undocumented default

| ID | Decision | Why deferred | Required evidence or trigger | Decision authority |
|---|---|---|---|---|
| DD-001 | Programming language and primary runtime | Architecture obligations must precede ecosystem preference | Walking-skeleton needs, module enforcement, determinism, packaging, security, and operations evaluation | Architecture authority |
| DD-002 | Build system and repository layout syntax | Depends on language and fitness tooling | Candidate proof that ADR-0003 and ADR-0005 can be enforced | Architecture authority |
| DD-003 | Persistence technology | Ownership and durability semantics must be decided before product selection | Workload model, transaction boundaries, dataset scale, recovery objectives, migration evidence | Architecture authority and data owner |
| DD-004 | Inter-module communication model | Direct calls and mediated messaging have meaningful consistency and complexity tradeoffs | Capability interaction map, transaction requirements, workflow durability, observability needs | Architecture authority |
| DD-005 | Event model and event-sourcing boundaries | Replay requirements do not imply universal event sourcing | Aggregate invariants, audit needs, integration boundaries, replay and migration scenarios | Architecture authority and domain owners |
| DD-006 | Extension isolation model | In-process, process, sandbox, and remote models differ materially in security and usability | Extension use cases, threat model, performance budget, supported languages, permission model | Architecture and security authorities |
| DD-007 | UI framework | Presentation technology does not alter current domain governance | Target platforms, accessibility, visualization performance, packaging, team capability | Architecture and product authorities |
| DD-008 | ML framework and model-serving technology | Model contracts are more durable than framework choice | Initial model classes, reproducibility, hardware targets, packaging and isolation needs | ML capability owner and architecture authority |
| DD-009 | Workflow engine | Workflow semantics must precede engine selection | Durability, scheduling, concurrency, checkpoint, replay, deployment and recovery needs | Workflow owner and architecture authority |
| DD-010 | Numeric RTO, RPO, availability, and performance budgets | Unsupported numbers would be fictional at M0 | Deployment topology, workload forecasts, business impact analysis, measured baselines | Product, operations, and architecture authorities |
| DD-011 | Serialization and API protocols | Contract-family governance is protocol-independent | Client landscape, streaming needs, schema tooling, compatibility and security evaluation | Contract owners and architecture authority |
| DD-012 | Identity provider and cryptographic implementation | Security outcomes are defined but deployment environment is not | Deployment model, compliance needs, trust topology, rotation and recovery exercises | Security authority |

## Rules

- A deferred decision must not be resolved implicitly by prototype code.
- Experiments may compare candidates but cannot establish an authoritative default without the required ADR or approved specification.
- Each decision is revisited when its trigger becomes true or before implementation would otherwise depend on it.
- New material alternatives, risks, and evidence are appended to the corresponding decision record.
