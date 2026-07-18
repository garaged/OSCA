# ADR-0022 — M2 Source-Evidence Retention Default

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, data, licensing, security, and architecture authorities
- **Scope:** M2 provider acquisition, source evidence, normalization, cleanup, backup, export, and reproducibility
- **Related requirements:** REQ-0028, REQ-0031–REQ-0033, REQ-0039
- **Related product decisions:** D-014, D-015, D-017, D-040
- **Supersedes:** None
- **Superseded by:** None

## Context

M2 needs a deterministic default when provider policy explicitly allows local retention. Retained source evidence improves parser diagnosis, correction, re-normalization, and reproducibility, but retention cannot be inferred from technical accessibility and must remain governed by the exact applicable provider policy.

## Decision

M2 retains immutable checksummed source evidence by default only when the exact active provider-policy revision explicitly permits acquisition and retention for the applicable account, plan, use, and jurisdiction.

If retention is prohibited or uncertain, M2 retains no provider payload. It records a metadata-only non-retention record containing provider, request, retrieval time, parser/build, policy revision, integrity information available without retaining prohibited content, and the reason/operation restrictions.

Retained source evidence:

- is stored separately from canonical payloads under ADR-0017 and ADR-0021;
- is never silently transformed or overwritten;
- carries acquisition, retention, transformation, export, backup, redistribution, and fixture rights independently;
- is included in backup only when backup rights are also explicit under ADR-0018;
- is excluded from export, redistribution, or fixtures unless those rights are independently explicit;
- may be removed only through preview-first cleanup after pins, lineage, recovery, reproducibility, and policy obligations are evaluated.

A policy change does not silently legalize or delete existing material. It triggers a governed review and, when required, a scoped cleanup plan with retained audit evidence.

## Consequences

Permitted acquisitions maximize reproducibility and parser-debug evidence. Storage use increases and provider-policy metadata becomes operationally critical. Providers that do not permit retention remain usable only if the accepted contract and canonicalization policy allow metadata-only evidence without violating transformation or derived-data restrictions.

## Fitness and verification

- explicit permitted policy retains a byte-identical checksummed source object;
- prohibited, absent, ambiguous, expired, or mismatched policy retains no payload;
- backup/export/fixture operations independently enforce their rights flags;
- policy changes produce review findings rather than silent mutation;
- cleanup preview protects pinned or reproducibility-required source objects;
- tests use synthetic or explicitly redistributable fixtures only;
- logs, diagnostics, and manifests contain no credential values.

## Revisit triggers

Provider terms or plan change, storage observations exceed the M2 envelope, retained evidence creates unacceptable licensing exposure, M3 introduces new source layers, or reproducibility objectives change.
