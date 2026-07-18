# M2 Initiation Record

- **Status:** Accepted for entry-decision work
- **Governing roles:** Product, architecture, security, data, licensing, and quality authorities
- **Baseline:** `979ae16a4271a8e8a5cbb29313b8ee9b1ca9b7af`
- **Requirements:** REQ-0021–REQ-0040
- **Specification:** [M2 governed daily market data](../../specifications/m2-governed-daily-market-data.md)
- **Accepted:** 2026-07-18

## Approved package

- [x] Repository-backed gap analysis precedes planning.
- [x] Thin user-visible stock-and-crypto daily-data intent and M2/M3 boundary are explicit.
- [x] REQ-0021–REQ-0040 retain exact PRD and D-record authority.
- [x] Instrument, Provider, Market Data, Catalog, Workflow, Operations, Recovery, and interface ownership is allocated.
- [x] Public contract candidates, security/failure behavior, licensing, cleanup, migration, and recovery boundaries are specified.
- [x] M2-AC-001–M2-AC-020 and high-risk evidence gates are accepted.
- [x] License-safe deterministic fixture policy is accepted.
- [x] Ten M2 risks have treatments, owners, and triggers.
- [x] Provider and persistence selections are evidence-gated rather than implied.
- [x] Traceability, navigation, architecture activity, and registry are reconciled.

## Approval meaning

The authorities accept the M2 intent, scope, requirements allocation, specification, evidence plan, execution sequence, risk treatments, and selection criteria. OpenSpec remains an execution view and did not grant approval.

Approval does not select a provider, authorize unreviewed provider use, select M2 payload persistence, or satisfy M2.0 completely.

## Remaining M2.0 gates

- accept exact semantic/structural public schemas and catalog entries;
- accept the metadata/payload persistence ADR and migration/recovery profile;
- accept the bounded daily expected-date policy;
- select reference providers only after provider-specific official-access, licensing, quota, credential, semantic, fixture, and failure review;
- approve provider-specific policy records before production-visible adapter work.

Deterministic contract and fixture work may proceed only where it does not establish a hidden provider, persistence, or M3 default. M2.1 persistent implementation remains blocked until its persistence decision is accepted.

## Decision

M2 governed initiation is accepted. The next authorized work is M2.0 entry-decision resolution, beginning with exact contracts and persistence/provider evidence—not product implementation.
