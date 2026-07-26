# P4 - No-Cost Provider Adapter Contracts

- **Status:** In review
- **Governing role:** Product authority
- **Architecture, licensing, data, operations, and quality review:** Required for P4 scope
- **Authoritative outcome:** Fixture-backed adapter contract readiness for SEC EDGAR and FRED
- **Baseline:** Completed M0-M12 roadmap and P1-P3 no-cost provider governance
- **Last reviewed:** 2026-07-26

## Current artifacts

- [Intent](intent.md)
- [Scope](scope.md)
- [Acceptance criteria](acceptance.md)
- [Evidence plan](evidence-plan.md)
- [Execution plan](execution-plan.md)
- [Risk register](risk-register.md)
- [P4 status](status.md)
- [Exit review](exit-review.md)
- [P4 no-cost provider adapter contracts specification](../../specifications/p4-no-cost-provider-adapter-contracts.md)
- [Manual testing and usage](../../testing/manual-testing.md)
- [Requirements catalog](../../governance/requirements-catalog.md)
- [Traceability register](../../governance/traceability-register.md)
- [Accepted P4 OpenSpec specification](../../../openspec/specs/p4-no-cost-provider-adapter-contracts/spec.md)
- [Archived P4 OpenSpec change](../../../openspec/changes/archive/2026-07-26-p4-no-cost-provider-adapter-contracts/README.md)

## Required chain

Intent -> Requirements -> Architecture -> Specification -> Validation -> Evidence

P4 turns the P3 preferred no-cost provider profiles into deterministic adapter contracts for SEC EDGAR and FRED. It defines requests, fixture validation, and provider-specific contract constraints. It does not invoke provider APIs, materialize credentials, alter runtime routing, promote providers, or enable production ingestion.
