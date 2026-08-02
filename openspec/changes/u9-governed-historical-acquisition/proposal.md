# U9 Governed Historical Acquisition

## Why

U8 proved that OSCA can run a complete local research, diagnostic, and human-gated validation workflow, but the principal equity demonstration still depends on an external data-preparation script. A usable release needs a first-class, no-cost acquisition path governed by OSCA's existing provider, licensing, provenance, canonical-storage, quality, and evidence requirements.

## Governing intent

Implement [U9 Governed No-Cost Historical Data Acquisition](../../../docs/milestones/u9/README.md) as the first milestone in the [U9-U14 usable release roadmap](../../../docs/milestones/usable-release-roadmap.md).

## Requirements

REQ-0021, REQ-0023 through REQ-0038, REQ-0041, REQ-0042, and the universal evidence-based milestone exit gate.

## Owning capabilities

- Provider governance and capability routing
- Instrument identity and mapping
- Market-data retrieval and normalization
- Workflow/job lifecycle
- Catalog and canonical storage
- Security and secrets
- Operations and observability
- CLI adapter

## Affected contract families

- Provider capability and provider policy
- Canonical instrument and provider mapping
- Historical retrieval request and structured resolution status
- OHLCV observations and dataset revisions
- Quality findings
- Job status and evidence metadata
- Primary CLI contracts

## Governing ADRs

Use the active provider, storage, security, workflow, evidence, and ADR-0044 execution-boundary decisions. This change does not supersede any ADR.

## Risk class

Medium-high because the change introduces bounded network retrieval and provider-policy enforcement, but it does not introduce recommendations or execution authority.

## What changes

- Add a provider-neutral historical-acquisition application capability.
- Expose it through a discoverable primary `osca` CLI command.
- Admit Kraken public market data and one no-cost equity source only when exact provider evidence passes the admission gate.
- Normalize successful retrievals through the existing canonical OHLCV and dataset-revision path.
- Retain capability, request, attribution, policy, integrity, quality, and outcome evidence.
- Preserve local CSV import as the offline fallback.
- Add deterministic failure handling for unsupported capability, quota, outage, policy uncertainty, malformed responses, and partial results.
- Prove compatibility with the U8 research pipeline and analyst workspace discovery.

## Explicit non-goals

- Investment recommendations
- Live model serving or automatic promotion
- Broker or exchange-order connectivity
- Autonomous or real-capital execution
- Paid-provider dependency for the principal demonstration
- Silent provider fallback or cross-provider series merging
- Broad provider expansion
- New analytical or ML model families

## Consequential decision gate

The exact no-cost equity source is not selected by this proposal. Selection requires current, retained evidence for licensing, account requirements, quotas, historical depth, adjustment semantics, retention, export, backup, redistribution, and attribution. If no candidate passes, implementation must fail closed and retain the blocked decision rather than adopt an ungoverned source.

## Success evidence

- Provider-admission evidence
- Contract and conformance tests
- Golden fixtures
- Security and secret-exclusion tests
- Failure and recovery tests
- CLI/API and storage evidence
- End-to-end Kraken acquisition
- End-to-end equity acquisition when admitted
- CSV fallback equivalence
- U8 pipeline compatibility
- Clean-profile manual acceptance record
