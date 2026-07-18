# ADR-0018 — M2 Market-Data Recovery Profile

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture, data, recovery, security, and licensing authorities
- **Scope:** M2 instrument/provider/catalog metadata and source/canonical daily payload backup and restore
- **Related requirements:** REQ-0028, REQ-0031–REQ-0033, REQ-0039, REQ-0040
- **Related product decisions:** D-014, D-015, D-017, D-040
- **Supersedes:** None
- **Superseded by:** None

## Context

ADR-0017 separates transactional M2 metadata in SQLite from immutable source and canonical payloads in Parquet. A consistent recovery profile must state which layers are protected without assuming provider data can always be retained, backed up, redistributed, or reacquired.

Metadata-only recovery could leave accepted canonical history unavailable or impossible to reproduce when source retention is prohibited, upstream history changes, mappings are corrected, or a provider disappears. Unconditionally backing up source material could violate provider policy.

## Decision

M2 backups always include the governed consistency marker and required Instrument, Provider, Market Data, Catalog, Workflow, Operations, policy, mapping, manifest, lineage, quality, audit, and recovery metadata.

M2 backups include every accepted canonical Parquet payload referenced by the selected consistency marker unless the backup is explicitly rejected as incomplete. Accepted canonical history is protected data, not a reconstructable cache.

Retained source Parquet payloads are included only when the exact recorded provider-policy revision explicitly permits backup. When source backup is prohibited or uncertain:

- the source payload is excluded;
- the manifest records intentional exclusion, provider, request, retrieval, parser, integrity, and policy identities;
- canonical payload, normalization revision, lineage, and available source evidence metadata remain protected;
- backup inspection and restore preview disclose the reproducibility limitation;
- no operation represents excluded source material as recovered or reconstructable.

Secrets, credential values, transient staging objects, quarantined unknown material, and provider content whose policy is uncertain remain excluded.

## Consistency and restore

Backup selection is manifest-driven at one durable consistency marker. The backup fails closed if required metadata or canonical objects are missing, corrupt, digest-invalid, outside the marker, or change during capture.

Restore verifies container integrity, compatibility, metadata migrations, Parquet schema versions, object digests, provider-policy records, and manifest/object reconciliation in isolation before activation. It reports restored, intentionally excluded, unavailable, corrupt, and policy-blocked material separately. Active state remains unchanged until validation succeeds.

Cleanup cannot delete canonical payloads protected by a retained backup/recovery requirement. Source cleanup respects policy, pins, reproducibility requirements, and manifest dependencies.

## Consequences

Canonical daily history is recoverable without depending on provider availability. Backup size grows with accepted canonical data. Source-level reproducibility may remain limited when rights prohibit backup, but that limitation is explicit and cannot be silently upgraded into a completeness claim.

## Fitness and verification

- backup planning selects exact metadata and canonical identities at one marker;
- missing or mutated canonical objects reject backup;
- policy-permitted source objects round-trip with verified digests;
- prohibited/uncertain source objects are excluded with complete non-retention evidence;
- isolated restore reconciles every manifest and reports exclusions;
- secret and policy canaries prove forbidden content is absent;
- cleanup preview protects recovery-required canonical objects;
- recovery documentation states size, rights, exclusions, and residual reproducibility limits.

## Revisit triggers

Accepted canonical volume exceeds the bounded local backup envelope, incremental backup is required, provider policy changes, M3 introduces new layers, recovery objectives change, or evidence shows the consistency-marker protocol is insufficient.
