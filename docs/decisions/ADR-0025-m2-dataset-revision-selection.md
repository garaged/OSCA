# ADR-0025 — M2 Dataset Revision Selection

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, architecture, and data authorities
- **Scope:** M2 retrieval requests, resolution, canonical datasets, reproducibility, catalog inspection, and cleanup protection
- **Related requirements:** REQ-0032–REQ-0036, REQ-0039
- **Related product decisions:** D-017, D-018
- **Supersedes:** None
- **Superseded by:** None

## Context

Canonical corrections create immutable revisions under ADR-0024. Ordinary users need a useful default, while reproducible workflows must be able to resolve the same accepted history after newer revisions exist.

## Decision

An M2 retrieval request may either omit a dataset revision or pin one exact accepted revision identity.

An unpinned request resolves the latest accepted revision satisfying the request's instrument, range, provider constraints, freshness, completeness, policy, and quality requirements. The resolution always returns the exact resolved dataset and revision identities; “latest” is never persisted as if it were an immutable identity.

A pinned request resolves only the named revision. It never silently substitutes a newer revision. If the revision is unavailable, corrupt, policy-blocked, incompatible, or does not satisfy the request, resolution returns that structured state and safe remediation.

New revisions can change future unpinned results but never mutate, hide, or redirect an earlier revision. Pinned revisions become protected dependencies for cleanup while the pin or reproducibility obligation remains active.

## Consequences

Interactive and ordinary automation remain convenient. Reproducible workflows can replay exact accepted datasets. Callers that need stability must retain or declare the returned revision identity rather than assuming future unpinned retrieval is unchanged.

## Fitness and verification

- unpinned retrieval deterministically selects the latest satisfying accepted revision;
- every successful resolution returns exact dataset/revision identity;
- pinned retrieval returns only the named revision;
- unavailable or invalid pins fail visibly without fallback;
- publishing a correction changes eligible unpinned resolution but not pinned resolution;
- cleanup preview protects active pinned revisions;
- interface adapters expose equivalent pinning and resolution semantics.

## Revisit triggers

M3 introduces multi-layer reconciliation selection, product requirements change default resolution, or evidence shows latest-accepted ordering is ambiguous.
