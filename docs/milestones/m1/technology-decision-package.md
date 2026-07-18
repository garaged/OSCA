# M1 Technology Decision Package

- **Status:** Accepted
- **Governing role:** Architecture authority
- **Product approval:** Product authority for user/deployment consequences
- **Purpose:** Resolve only the technology decisions triggered by the M1 secure walking skeleton.
- **Authoritative sources:** M1 intent and scope; DD-001, DD-002, DD-003, DD-009, DD-011, DD-012; ADR-0002 through ADR-0010
- **Last reviewed:** 2026-07-18

## Recommended coherent set

| Concern | Recommendation | Why it fits M1 |
|---|---|---|
| Runtime | Python 3.13, CPython | Best alignment with OSCA's future quantitative/ML ecosystem; mature typing, async I/O, packaging, testing, and observability support. |
| Dependency/build | `uv` with locked dependencies and PEP 621 `pyproject.toml` | Fast reproducible local setup, one tool for environments/locking/execution, and low contributor friction. |
| Repository shape | One Python distribution with top-level capability packages under `src/osca/`, explicit public `api` modules, and boundary tests | Enforces the modular monolith without premature multi-package release/versioning overhead. |
| HTTP API | FastAPI with explicit `/api/v1` routing and generated OpenAPI 3.1 | Typed validation, structured errors, async support, and strong contract/tooling ecosystem. |
| CLI | Typer adapter invoking the same application services | Type-aligned CLI with no duplicated business rules. |
| M1 web shell | Server-rendered semantic HTML using Starlette/Jinja templates plus minimal progressive enhancement | Delivers the required web shell without triggering a permanent SPA/framework decision before visualization needs are known. |
| Metadata/job persistence | SQLite in WAL mode through SQLAlchemy 2 and Alembic migrations | Zero-service local operation, transactional metadata, portable backups, and an abstraction boundary for later evidence-driven change. |
| Market payload posture | No market-data payload store in M1; preserve a separate future data-storage decision | Avoids choosing M2/M3 analytical storage from M1 metadata needs. |
| Durable jobs | OSCA-owned database-backed job lifecycle and single-node executor | Satisfies embedded/local-first durability without Redis, a broker, or an external workflow service; semantics remain owned by OSCA. |
| Contract representation | Pydantic v2 semantic models and JSON Schema/OpenAPI for HTTP; versioned JSON records for retained M1 contracts | One typed semantic source with executable schema/compatibility fixtures. |
| Secrets | `keyring`-backed operating-system credential adapter behind an OSCA vault port; test-only in-memory adapter | Uses native credential stores, preserves replaceability, and avoids inventing cryptography for ordinary secrets. |
| Telemetry | Standard logging with structured JSON plus OpenTelemetry APIs/SDK; built-in health remains independent of external collectors | Supports correlation and optional export without requiring external observability infrastructure. |
| Testing | pytest, Hypothesis, mypy strict baseline, Ruff, import-boundary checks, contract fixtures, and Playwright only for critical web journeys | Implements risk-tiered evidence with strong Python-native tooling. |
| Documentation | MkDocs Material with executable command/example verification in CI | Versioned task guidance and generated reference integration without replacing conceptual documentation. |
| Packaging | Local development command first; OCI container profile introduced only for personal-server verification | Keeps workstation startup simple while proving server packageability. |

## Persistence rationale

SQLite is recommended only for M1 configuration, metadata, job, audit, and recovery state. It is not selected as the future time-series analytical engine. WAL mode, short transactions, one-writer discipline, busy-timeout policy, integrity checks, and migration/backup tests are mandatory.

A database-backed executor is intentionally smaller than Celery, Temporal, or another external scheduler. M1 requires durable semantics and four-job future capacity, not distributed orchestration. The public workflow contract prevents the executor implementation from becoming domain authority.

## Security-profile recommendation

- Local profile binds to `127.0.0.1` and `::1` by default.
- Non-loopback binding is rejected unless the personal-server profile is explicitly selected.
- The personal-server skeleton requires configured TLS material and an authenticated application-session provider before startup succeeds.
- M1 does not claim production internet-hardening or multi-user security.
- Secret values are never serialized into application configuration or ordinary backup content.
- Backup encryption format should be decided in the recovery specification after evaluating interoperable, reviewed formats; M1 code must not invent an ad-hoc cipher container.

## Alternatives considered

### Polyglot Python API plus TypeScript SPA

This better anticipates rich dashboards but adds two build systems, duplicated contract-generation concerns, browser dependency management, and a premature DD-007 commitment before M1 has visualization behavior. Defer until M4 unless evidence emerges earlier.

### PostgreSQL from M1

It improves concurrency and server parity but violates the zero-service workstation experience and adds installation, credential, backup, and upgrade operations before M1 proves product value. Revisit when measured workload or personal-server concurrency exceeds SQLite's governed envelope.

### Celery, Dramatiq, or RQ

They offer mature queues but introduce a broker or backend topology and do not by themselves define OSCA's workflow identity, checkpoint, compatibility, and recovery semantics. An adapter may be considered later when parallel workload evidence justifies it.

### Temporal or another external workflow engine

It provides strong durability but imposes substantial operational infrastructure and deployment coupling inconsistent with the initial local-first single-node product.

### Custom encrypted secret file

It reduces OS-specific behavior but creates cryptographic key lifecycle, format, rotation, and recovery obligations unnecessarily. Native credential stores behind a port are safer for M1.

## Decision consequences

If accepted, the package should be split into focused ADRs:

1. runtime, dependency, and repository-boundary enforcement;
2. M1 metadata persistence and migration;
3. embedded durable-job implementation;
4. M1 contract and interface representation;
5. local-owner security and secret-vault implementation profile.

The web-shell choice remains explicitly provisional adapter guidance rather than a foundational UI-framework ADR.

## Approval record

The recommended coherent set was accepted by the product and architecture authority on 2026-07-18 and formalized as ADR-0011 through ADR-0015.
