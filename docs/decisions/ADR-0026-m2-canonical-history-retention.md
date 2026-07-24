# ADR-0026 — M2 Canonical-History Retention

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, architecture, data, and licensing authorities
- **Scope:** M2 canonical revisions, cleanup, pins, recovery, reproducibility, and storage inspection
- **Related requirements:** REQ-0032, REQ-0033, REQ-0039
- **Related product decisions:** D-014, D-015, D-017
- **Supersedes:** None
- **Superseded by:** None

## Decision

Every accepted M2 canonical dataset revision is protected for the duration of M2. Cleanup cannot delete, evict, compact away, or make unavailable accepted canonical history, regardless of whether it is latest or explicitly pinned.

M2 cleanup may address eligible staging, orphaned, corrupt/quarantined, and policy-permitted source material only after preview and dependency checks. Catalog metadata and lineage survive every payload cleanup.

This bounded policy avoids premature configurable canonical retention. Storage inspection reports the protected canonical footprint so M2 exit evidence can support a later policy decision.

## Consequences and fitness

Historical reproducibility and ADR-0025 pinned retrieval remain reliable at the cost of growing canonical storage. Tests prove cleanup plans exclude every accepted canonical manifest/object, preserve catalog lineage, and report protected bytes separately. Revisit after measured M2 storage evidence or when M3 accepts a broader retention policy.
