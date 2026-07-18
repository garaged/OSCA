# ADR-0014 — M1 Contract and Interface Representation

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture authority and contract owners
- **Scope:** M1 application contracts, HTTP API, CLI, retained records, and web shell
- **Related requirements:** REQ-0002 through REQ-0005, REQ-0011, REQ-0013, REQ-0015
- **Related product decisions:** D-021, D-022, D-035, D-046
- **Supersedes:** DD-011 for M1
- **Superseded by:** None

## Context

M1 introduces the first independently consumed and retained OSCA contracts. Web, CLI, and API behavior must remain semantically consistent and compatibility governed.

## Decision

M1 will use immutable Pydantic v2 semantic models as Python contract types. JSON Schema and OpenAPI 3.1 represent structural HTTP contracts. The HTTP API uses explicit `/api/v1` routing through FastAPI. Retained M1 JSON records declare contract family, major version, and exact revision.

The CLI uses Typer as a transport adapter invoking the same application services. The M1 web shell uses server-rendered semantic HTML through Starlette/Jinja templates with minimal progressive enhancement. This web choice is adapter-local and does not settle the M4 visualization framework.

Every public family defines owner, semantic invariants, error envelope, security classification, compatibility profile, schema, fixtures, and supported revisions before implementation relies on it.

Generated schemas supplement rather than replace semantic specifications.

## Consequences

One typed source reduces interface drift. Framework types remain outside domain authority. Pydantic models cannot become persistence entities or private-domain leakage. API version in the route does not replace per-family compatibility governance.

## Fitness

- semantic fixtures produce equivalent API and CLI outcomes;
- OpenAPI and JSON Schema generation are deterministic;
- compatibility fixtures exercise supported producer/consumer revisions;
- web handlers contain presentation behavior only;
- structured errors retain category, correlation, retryability, and safe remediation;
- unknown field/version behavior is explicitly tested.

## Revisit triggers

Streaming, binary payloads, independently released SDKs, notebook ergonomics, or visualization needs require a different representation.
