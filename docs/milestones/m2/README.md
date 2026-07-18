# M2 — Instruments, Providers, and Cache Vertical Slice

- **Status:** M2.3–M2.7 implementation in progress; provider production promotion remains policy-blocked
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
- [M2 operations guide](operations-guide.md)
- [Active consolidated OpenSpec change](../../../openspec/changes/m2-governed-daily-data/proposal.md)
- [M2.2 provider contract evidence](../../../evidence/m2/m2-2-provider-contract-fixtures.md)
- [Archived M2.2 OpenSpec change](../../../openspec/changes/archive/2026-07-18-m2-provider-contract/README.md)
- [Accepted M2 persistence ADR](../../decisions/ADR-0017-m2-metadata-and-daily-payload-persistence.md)
- [Accepted M2 recovery ADR](../../decisions/ADR-0018-m2-market-data-recovery-profile.md)
- [Accepted M2 numeric representation ADR](../../decisions/ADR-0019-m2-canonical-daily-bar-numeric-representation.md)
- [Accepted M2 expected-date ADR](../../decisions/ADR-0020-m2-bounded-daily-expected-date-policy.md)
- [Accepted M2 Parquet layout ADR](../../decisions/ADR-0021-m2-parquet-object-granularity-and-publication.md)
- [Accepted M2 source-retention ADR](../../decisions/ADR-0022-m2-source-evidence-retention-default.md)
- [Accepted M2 incomplete-observation ADR](../../decisions/ADR-0023-m2-incomplete-daily-observation-publication.md)
- [Accepted M2 canonical revision ADR](../../decisions/ADR-0024-m2-canonical-dataset-revision-identity.md)
- [Accepted M2 revision selection ADR](../../decisions/ADR-0025-m2-dataset-revision-selection.md)
- [Accepted M2 canonical-history ADR](../../decisions/ADR-0026-m2-canonical-history-retention.md)
- [Accepted generic durable-job ADR](../../decisions/ADR-0027-generic-durable-job-contract.md)
- [Accepted M2 authorization ADR](../../decisions/ADR-0028-m2-market-data-authorization-capabilities.md)
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
