# ADR-0021 — M2 Parquet Object Granularity and Publication

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture and data authorities
- **Scope:** M2 source/canonical Parquet objects, manifests, revisions, integrity, range reads, cleanup, and recovery
- **Related requirements:** REQ-0031–REQ-0033, REQ-0037, REQ-0039
- **Related product decisions:** D-014, D-015, D-017, D-018
- **Supersedes:** None
- **Superseded by:** None

## Context

ADR-0017 selects immutable Parquet payloads and SQLite manifests. M2 needs a bounded object unit that supports atomic publication, exact integrity, revision history, targeted repair, recovery, and cleanup without premature M3 partition optimization or a tiny-file explosion.

## Decision

Each M2 Parquet object represents exactly one layer, one canonical instrument, one provider/source context, one dataset revision, and one bounded start-inclusive/end-exclusive effective-date range.

Source and canonical layers use separate governed namespaces and manifests. A canonical correction or repair publishes a new object and dataset revision; it never mutates an accepted object. Unaffected lineage remains referenced explicitly.

Objects are written to a same-filesystem staging path, validated, durably closed, digested, atomically renamed to a content-addressed final path, and then exposed through a `ready` manifest under ADR-0017. Physical paths are private infrastructure and never enter public dataset identity.

M2 does not use one-file-per-day objects, implicit directory-partition identity, or mandatory yearly partitions. A bounded request may be split only when a configured object row/byte limit requires it; each resulting object remains explicit in the same dataset revision manifest and is published as one reconciled revision.

## Consequences

The layout makes publication, digest verification, backup selection, cleanup preview, and isolated restore straightforward. Corrections can duplicate unaffected rows in small M2 datasets, and long histories may scan more data than yearly partitioning. These are accepted M2 tradeoffs and must be measured before changing layout.

## Fitness and verification

- manifest uniqueness covers layer, instrument, provider/source, revision, and range;
- objects contain only rows within their declared range and context;
- staged or partially published objects are invisible to readers;
- corrections create new immutable objects and monotonically distinct revisions;
- digest/path tampering and overlapping conflicting objects are detected;
- bounded range reads return deterministic ordered rows;
- cleanup and recovery operate on exact manifest identities;
- performance evidence reports object counts, sizes, and bounded read/write observations.

## Revisit triggers

Measured M2 object size/count or read amplification exceeds the accepted envelope, M3 analytical storage is accepted, incremental backup requires subdivision, or filesystem behavior invalidates atomic publication assumptions.
