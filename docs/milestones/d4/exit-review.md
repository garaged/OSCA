# D4 Exit Review — Asset Catalog, Market Browser, and Watchlists

- **Status:** Accepted
- **Pull request:** #84
- **Baseline:** D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`

## Delivered outcome

D4 adds an offline-first Markets area with canonical asset identities, deterministic search, explicit venue ambiguity, provider aliases, asset provenance, local-data availability summaries, profile-scoped recent assets, and persistent ordered watchlists.

Python remains authoritative for identity resolution, search, details, persistence, validation, and profile mutation locking. React continues to use the single narrow `desktop_request` bridge. Rust owns only the desktop broker/session lease needed to preserve window/process profile ownership across short-lived sidecar requests. No generic filesystem, database, HTTP, shell, provider, brokerage, or execution authority was added to React or Rust.

## Requirements and architecture disposition

Requirements `REQ-0309` through `REQ-0324` are allocated across the D4 specification, OpenSpec capability, implementation, tests, manual-acceptance procedure, traceability, and this exit review.

Canonical identity remains distinct from provider symbols. Exact collisions fail visibly through an ambiguity result. Watchlists store canonical IDs rather than display symbols, are isolated by profile, and retain deterministic member order. Mutations use profile ownership/locking and SQLite transactions. Supported external desktop-API mutations coordinate with the desktop lifetime lease and fail closed while another desktop owner holds the profile.

Disposition: pass.

## Automated validation disposition

Quality `31658374252` and Desktop Foundation `31658374251` passed on implementation candidate `08b1c00e32440022d57e7c659625bf7eac490bd8`. OpenSpec, secret scanning, Ruff, strict mypy, full Python tests, architecture checks, frontend build/tests, desktop API tests, Rust formatting/tests/Clippy, Linux packaged desktop build/smoke, and wheel-content verification passed.

A subsequent documentation/evidence reconciliation is subject to the same required hosted gates before merge.

Disposition: pass.

## Supported-platform manual acceptance

- macOS ARM64: PASS.
- Linux x86-64: PASS.

The accepted evidence covers deterministic catalog/search behavior, explicit ambiguity, details and recents, persistent ordered watchlists, duplicate rejection, restart persistence, same-profile ownership rejection, selection without ownership, supported external mutation rejection/acquisition, separate-profile isolation, no-network boundaries, accessibility/responsive behavior, self-contained native package launch, packaged persistence/ownership, and packaged responsiveness.

Manual testing also discovered and drove fixes for desktop lifetime profile ownership, direct CLI/session coordination, packaged-sidecar self-containment, PyInstaller one-file performance stalls, sidecar smoke timeout alignment, and macOS DMG overreach in the canonical acceptance build.

Disposition: pass.

## Safety and non-goals

D4 does not add streaming quotes, production charting, recommendations, alerts, portfolio ownership, broker or exchange connectivity, order entry, autonomous execution, live orders, or real-capital behavior. Catalog and watchlist operations remain offline-first and no paid provider is required.

Disposition: pass.

## Exit decision

All D4 implementation, automated-validation, and supported-platform manual-acceptance gates are satisfied. The repository owner explicitly authorized merge after both platform acceptance passes.

**D4 exit decision: ACCEPTED / MERGE READY**, subject to the final hosted CI result on the evidence-reconciliation head.
