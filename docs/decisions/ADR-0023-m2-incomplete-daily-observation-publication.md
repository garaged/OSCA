# ADR-0023 — M2 Incomplete Daily-Observation Publication

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, architecture, and data authorities
- **Scope:** M2 provider acquisition, source evidence, canonical daily bars, resolution state, freshness, revisions, and repair
- **Related requirements:** REQ-0030–REQ-0038
- **Related product decisions:** D-013, D-017, D-018
- **Supersedes:** None
- **Superseded by:** None

## Context

Providers may expose a current or otherwise incomplete daily observation. Publishing it canonically would introduce provisional-bar replacement semantics that the accepted M2/M3 boundary defers. Discarding it entirely would remove useful diagnostic evidence when source retention is permitted.

## Decision

An incomplete provider daily observation never enters an accepted M2 canonical dataset.

When ADR-0022 permits source retention, the exact incomplete response may be retained as immutable checksummed source evidence with completion state, retrieval identity, provider policy, parser/build, and integrity metadata. When retention is prohibited or uncertain, only the governed non-retention metadata record is stored.

A request affected by an incomplete observation resolves as `partial` or `refreshing` according to durable work state. It cannot resolve as fresh/complete, fabricate a completed bar, or silently reuse an earlier incomplete value.

When a later retrieval supplies a valid complete observation, normalization publishes it through the ordinary immutable canonical revision protocol. It does not mutate or promote the incomplete source object. Source and canonical lineage links make the transition visible.

M2 does not expose provisional canonical bars, provisional analytical inputs, or intraday session semantics.

## Consequences

Accepted canonical datasets contain complete daily observations only. Current-day availability may lag provider display behavior, but callers receive an honest structured state. Permitted source evidence remains useful for provider diagnosis without contaminating canonical history.

## Fitness and verification

- incomplete observations are absent from canonical Parquet objects;
- permitted incomplete source responses retain completion and integrity evidence;
- prohibited/uncertain retention stores no source payload;
- resolution is partial/refreshing and never fresh/complete;
- later completion creates a new canonical revision with explicit lineage;
- cancellation/restart cannot publish an incomplete staged object;
- no M2 interface exposes a provisional canonical bar.

## Revisit triggers

M3 accepts provisional/session semantics, product requirements explicitly require provisional daily bars, or provider completion evidence cannot be represented reliably.
