# ADR-0024 — M2 Canonical Dataset Revision Identity

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture and data authorities
- **Scope:** M2 normalization, canonical dataset identity, idempotency, lineage, revisions, manifests, repair, and catalog metadata
- **Related requirements:** REQ-0031–REQ-0037
- **Related product decisions:** D-017, D-018
- **Supersedes:** None
- **Superseded by:** None

## Context

M2 must avoid both silent canonical mutation and meaningless revision growth. Creating a revision for every retrieval would produce noise when nothing changed. Comparing only OHLCV values would hide meaningful changes in source evidence, mapping, parser, normalization, or governed configuration.

## Decision

M2 uses content-sensitive idempotent canonical revision identity.

A canonical identity fingerprint deterministically covers:

- canonical instrument and interval;
- bounded range and ordered complete daily-bar content;
- source evidence identities and integrity digests or governed non-retention records;
- provider and verified mapping identities/revisions;
- parser and normalizer identities/versions;
- governed configuration and policy revisions;
- canonical schema major/revision and relevant build identity.

When an accepted dataset with the same fingerprint already exists, equivalent work returns that existing dataset revision and does not publish another Parquet object or manifest revision.

Any fingerprint change creates a distinct immutable monotonically ordered revision with lineage to affected prior revisions and source evidence. Values need not change for a meaningful mapping, parser, source, policy, schema, or configuration change to require a new revision.

Retrieval time, correlation identity, attempt count, and other execution-only metadata do not change canonical identity; they remain workflow/audit evidence linked to the reused or created revision.

## Consequences

Retries and equivalent concurrent work converge without revision noise. Semantically meaningful provenance changes remain visible even when bar values match. Fingerprint construction becomes a governed compatibility surface and must remain deterministic across processes and supported platforms.

## Fitness and verification

- identical normalized inputs across retries/processes reuse one revision;
- reordered equivalent input produces the same ordered canonical fingerprint;
- changes to any governed identity input create a new revision;
- execution-only metadata does not create a revision;
- no accepted object is overwritten;
- concurrent equivalent publication resolves to one ready manifest;
- repair preserves unaffected lineage while changing the fingerprint only where governed inputs differ;
- catalog and audit evidence distinguish reuse from new publication.

## Revisit triggers

Fingerprint computation is non-deterministic, revision reuse hides required evidence, M3 introduces layered reconciliation identity, or concurrency evidence shows the uniqueness protocol is insufficient.
