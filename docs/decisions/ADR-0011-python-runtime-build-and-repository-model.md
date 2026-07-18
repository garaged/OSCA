# ADR-0011 — Python Runtime, Build, and Repository Model

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture authority and repository maintainers
- **Scope:** M1 runtime, dependency management, build, source layout, and module-boundary enforcement
- **Related requirements:** REQ-0001, REQ-0002, REQ-0019, REQ-0020
- **Related product decisions:** D-006, D-007, D-021, D-044, D-046
- **Supersedes:** DD-001 and DD-002 for the initial implementation
- **Superseded by:** None

## Context

M1 creates OSCA's first runnable product. ADR-0002 and ADR-0003 require a modular monolith with mechanically enforceable public/private boundaries, while the local-first quantitative roadmap requires a mature numerical, data, ML, testing, and packaging ecosystem.

## Decision

OSCA will use CPython 3.13 and one Python distribution managed by `uv` through a locked PEP 621 `pyproject.toml`.

Production source lives under `src/osca/`. Logical capabilities use top-level packages with explicit public `api` modules and private implementation packages. Capability code may depend only on published application contracts, shared-kernel primitives explicitly admitted by architecture, and inward-owned ports.

Boundary enforcement will combine:

- import-boundary rules;
- strict static typing baseline;
- package/API visibility conventions;
- cycle detection;
- architecture tests;
- test fixtures that consume public contracts rather than private implementations.

M1 uses one distribution rather than independently released capability packages. Independent packaging remains available later if enforcement evidence shows one distribution is insufficient.

## Consequences

Python aligns with future quantitative and ML work and keeps one primary runtime. `uv` provides deterministic environments, locking, commands, and packaging. A single distribution reduces early release complexity but requires strong automated import controls.

Python's runtime dynamism cannot be treated as permission to bypass boundaries through reflection, dependency injection, or service location.

## Alternatives

- A polyglot Python/TypeScript foundation was rejected for M1 because two toolchains add contract and build complexity before rich visualization exists.
- Multiple Python distributions were rejected because release/version coordination would exceed current enforcement needs.
- JVM, Rust, and Go were not selected as the primary runtime because their strengths do not outweigh Python ecosystem alignment for OSCA's initial product.

## Fitness

- locked environment reproduces from a clean checkout;
- forbidden cross-capability imports fail CI;
- module dependency graph is acyclic;
- public adapters consume application contracts;
- mypy strict baseline and Ruff checks pass;
- source packages are importable only through declared dependency policy.

## Revisit triggers

Revisit if Python prevents an accepted performance, isolation, packaging, or security objective after profiling, or if independent capability release requires physical package separation.
