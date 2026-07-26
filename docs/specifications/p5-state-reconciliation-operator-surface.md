# P5 State Reconciliation and Operator Surface Specification

## Purpose

Reconcile M0-M12 and P1-P4 documentation, specifications, traceability, and implementation boundaries, then expose the existing provider catalog and adapter-contract state through operator-facing CLI/API commands.

## Phase

Minimum usable local/demo tool

## User-visible value

Maintainers can see exactly what is complete, specified, fixture-backed, deferred, and ready for the next implementation slice.

## Requirements

- REQ-0191-REQ-0197: OSCA must implement the P5 scope described by this specification before P5 is marked complete.
- REQ-0191-REQ-0197: P5 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0191-REQ-0197: P5 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Review M0-M12 and P1-P4 docs, specs, ADRs, traceability, manual tests, and source layout for drift or partial implementation claims.
- Fix stale status, navigation, architecture registry, ADR index, traceability, and manual-testing references found during review.
- Add CLI inspection paths for provider production evidence gates, no-cost provider profiles, adapter contracts, and fixture-validation outcomes.
- Add tests proving operator surfaces report deferred live-provider, runtime-routing, credential, production-ingestion, and real-capital boundaries.

## Explicit non-scope

- Live provider calls.
- Credential materialization.
- Runtime provider routing.
- Production ingestion.
- Real-capital orders.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P1-P4 provider governance and completed M0-M12 roadmap.

## Risks and decisions

Review may uncover implementation drift that requires small corrective patches before operator surfaces are trustworthy.


## Operator commands

P5 exposes the existing P1-P4 provider governance state through these CLI commands:

| Command | Purpose | Boundary |
|---|---|---|
| `provider-catalog-list --include-readiness` | Lists no-cost provider profiles and deterministic implementation readiness. | Does not implement provider adapters or invoke providers. |
| `provider-promotion-status` | Lists production promotion candidates and required evidence classes. | Keeps provider enablement false without accepted evidence. |
| `provider-adapter-contracts` | Lists fixture-backed SEC EDGAR and FRED adapter contracts. | Keeps network access disabled. |
| `provider-adapter-validate-fixture` | Validates fixture metadata against adapter contracts. | Validates metadata only; does not fetch live data. |
