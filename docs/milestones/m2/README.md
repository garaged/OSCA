# M2 — Instruments, Providers, and Cache Vertical Slice

- **Status:** M2.1 instrument registry implemented; provider/licensing decisions remain pending
- **Governing role:** Product authority
- **Architecture, security, data, licensing, and quality review:** Required
- **Authoritative outcome:** PRD M2
- **Baseline:** Accepted M1 secure walking skeleton
- **Last reviewed:** 2026-07-18

## Current artifacts

- [Repository-backed initiation gap analysis](gap-analysis.md)
- [Accepted intent](intent.md)
- [Accepted scope](scope.md)
- [Accepted specification](../../specifications/m2-governed-daily-market-data.md)
- [Accepted evidence plan](evidence-plan.md)
- [Accepted execution plan](execution-plan.md)
- [Accepted entry decisions](entry-decisions.md)
- [Accepted staged provider strategy](provider-strategy.md)
- [Accepted M2 persistence ADR](../../decisions/ADR-0017-m2-metadata-and-daily-payload-persistence.md)
- [M2.1 instrument registry evidence](../../../evidence/m2/m2-1-instrument-registry.md)
- [Archived M2.1 OpenSpec change](../../../openspec/changes/archive/2026-07-18-m2-instrument-registry/README.md)
- [Active risk register](risk-register.md)
- [Requirements catalog](../../governance/requirements-catalog.md)
- [Traceability register](../../governance/traceability-register.md)
- [M2 initiation record](initiation-record.md)
- [Archived M2 initiation OpenSpec change](../../../openspec/changes/archive/2026-07-18-m2-initiation/README.md)

## Required initiation sequence

Intent → Requirements → Architecture → Specification → Validation → Evidence

ADR-0017 authorizes M2.1 metadata implementation and governs later Parquet payload work. Provider selection and production-visible adapters remain gated by provider-specific licensing and policy approval. Deterministic fixture-first contract work may proceed.
