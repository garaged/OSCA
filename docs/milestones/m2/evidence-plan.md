# M2 Evidence Plan

- **Status:** Proposed
- **Governing role:** Quality authority
- **Security, data, licensing, and architecture approval:** Required
- **Governing specification:** [M2 governed daily market data](../../specifications/m2-governed-daily-market-data.md)
- **Last reviewed:** 2026-07-18

## Risk classification

M2 is a governed high-risk change because external providers, licensing policy, canonical financial observations, persistent revisions, untrusted payloads, quotas, cleanup, and migrations can cause disclosure, rights violations, silent corruption, or irreproducible research.

## Required gates

- locked environment, Ruff, strict mypy, full tests, architecture boundaries, links, schemas, migrations, OpenSpec, and secret scan;
- instrument identity/mapping schema, property, ambiguity, lifecycle, and correction suites;
- provider adapter conformance with deterministic recorded/synthetic fixtures and no required live-network CI;
- routing, fallback visibility, quota, licensing, credential-reference, timeout, retry, size, SSRF, decompression, and malformed-payload negatives;
- daily-bar golden fixtures, decimal/temporal semantics, deterministic normalization, revision, integrity, and lineage tests;
- freshness/completeness resolution properties, concurrent idempotency, restart, cancellation, gaps, and targeted repair;
- quality rule properties and finding/audit/telemetry assertions;
- persistence ownership and upgrade/downgrade/reconciliation tests;
- inspection and cleanup preview/protection tests;
- CLI/API semantic end-to-end path for stock and crypto fixtures;
- bounded cached/indexed performance observations;
- executable documentation and accessibility inspection for affected web behavior.

## Fixture policy

Fixtures must be license-safe, immutable, checksummed, minimal, and attributed. Prefer synthetic semantic fixtures plus provider-approved recorded metadata/payloads. A live provider response cannot be the only evidence for a contract. Secrets and restricted payloads cannot enter the repository or CI artifacts.

## Evidence retention

Retain records under `evidence/m2/` with source SHA, locked/tool versions, provider adapter/version, policy revision, fixture digests and rights, contract/schema revisions, migration revisions, results, limitations, exceptions, residual risks, and immutable CI identity.

## Merge policy

No slice merges with a failing applicable gate, unresolved critical data/licensing/security risk, unreviewed provider terms, or incomplete canonical compatibility/migration evidence. Exceptions use the governed `EXC-NNNN` process and cannot silently waive product or licensing authority.
