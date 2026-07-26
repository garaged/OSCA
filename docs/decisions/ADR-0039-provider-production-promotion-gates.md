# ADR-0039 - Provider Production Promotion Gates

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product and architecture authorities
- **Related requirements:** REQ-0157 through REQ-0166

## Context

M2 introduced provider-neutral data contracts and selected Twelve Data plus Kraken as the staged provider strategy, but production promotion for paid, authenticated, or license-sensitive provider use remained deferred. Later milestones repeatedly preserved that boundary because exact provider-specific licensing, account-plan, credential, quota, retention, export, backup, and policy evidence had not been accepted.

P1 starts the post-roadmap sequence by making that evidence explicit and testable before any provider is considered production-enabled.

## Decision

OSCA will represent provider production promotion through immutable evidence bundles and deterministic promotion decisions.

A production promotion evidence bundle must identify the provider, capability scope, licensing/account-plan permissions, named credential reference, credential verification status, quota policy, quota headroom, retention policy, export policy, backup policy, reviewer, review time, and findings.

A provider promotion decision may approve production enablement only when deterministic gates find no errors or warnings. Error findings block promotion. Warning findings defer promotion. Approved decisions must explicitly set production enablement; blocked or degraded decisions cannot enable production.

## Consequences

- Provider production promotion becomes traceable evidence rather than a configuration toggle.
- Uncertain licensing, credential, quota, retention, export, or backup policy evidence fails closed.
- Evidence can be retained and queried without storing secret values or calling providers in CI.
- Real provider calls, credential materialization, ingestion execution, and redistribution behavior remain separate governed work.
