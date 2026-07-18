# M1.1 Readiness Foundation Evidence

- **Status:** Complete
- **Source branch:** `agent/m1-secure-walking-skeleton`
- **Intent:** [M1 secure walking skeleton](../../docs/milestones/m1/intent.md)
- **Requirements:** REQ-0001–REQ-0008, REQ-0014–REQ-0016, REQ-0019, REQ-0020 (partial realization)
- **Specification:** [M1 secure walking skeleton](../../docs/specifications/m1-secure-walking-skeleton.md)
- **ADRs:** ADR-0001–ADR-0015
- **Risk class:** Governed high-risk foundation
- **Executed:** 2026-07-18
- **Executor:** Architecture/implementation agent

## Environment

- CPython 3.13.14 managed by `uv`
- locked dependency graph: `uv.lock`
- project version: `0.1.0.dev0`
- test environment created from the locked dependency set

## Evidence

| Criterion | Method | Result |
|---|---|---|
| Locked environment resolves under Python 3.13 | `uv lock --python 3.13`, `uv sync --locked --group dev` | Pass |
| Unit behavior | `uv run --group dev pytest` | 11 tests passed |
| Formatting/lint baseline | `uv run --group dev ruff check src tests` | Pass |
| Strict typing baseline | `uv run --group dev mypy` | Pass; 18 source files |
| CLI readiness | `uv run osca readiness` | Pass; versioned healthy snapshot emitted |
| API readiness | FastAPI TestClient `GET /api/v1/readiness` | Pass |
| Web readiness | FastAPI TestClient `GET /health` | Pass; semantic health content |
| Cross-interface equivalence | Contract fixture comparing API, CLI, and web | Pass |
| Unsafe local bind rejection | Unit negative test | Pass |
| Personal-server prerequisites | Unit positive and negative tests | Pass |
| Required health blocker aggregation | Unit test | Pass |

## Scope evidenced

- Python/uv/source-layout bootstrap;
- immutable Pydantic public contracts;
- loopback-safe configuration validation;
- fail-closed personal-server prerequisite validation;
- deterministic readiness aggregation;
- shared composition root used by CLI, API, and web;
- deterministic OpenAPI exposure and initial contract equivalence.

## Limitations and deferred evidence

- Module dependency tooling, database migrations, vault adapter, telemetry, durable jobs, catalog, backup/restore, executable documentation site, and CI workflow are later M1 increments.
- The execution environment emitted a workspace-specific virtual-environment symlink warning; it did not affect resolved versions or results.
- No architecture exception is active.

## Conclusion

The evidence supports completion of the M1.1 readiness foundation and entry into persistence, security/vault, telemetry, and durable-job increments. It does not support M1 milestone exit.
