# D4 Validation Evidence — Asset Catalog, Market Browser, and Watchlists

- **Status:** Automated validation passed; macOS ARM64 and Linux x86-64 manual acceptance passed
- **Pull request:** #84
- **Branch:** `agent/d4-asset-catalog-watchlists`
- **Baseline:** D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`
- **Validated implementation candidate:** `08b1c00e32440022d57e7c659625bf7eac490bd8`

## Automated validation

The current implementation candidate passed:

- Quality run `31658374252`;
- Desktop Foundation run `31658374251`;
- strict OpenSpec validation;
- secret scanning;
- Ruff and strict mypy;
- the full Python, contract, migration, link, and architecture suite;
- desktop API and launcher tests;
- frontend TypeScript build and Node test suite;
- Rust formatting, unit tests, and Clippy;
- Linux x86-64 packaged desktop build and smoke.

The suite contains focused D4 coverage for deterministic asset search, provider aliases, exact-symbol ambiguity, canonical identifiers, profile-scoped SQLite persistence, ordered watchlist membership, collision-safe reorder, typed offline desktop methods, narrow frontend authority, responsive layout, reduced motion, forced-colors safeguards, packaged-sidecar construction, broker/profile locking, and platform-specific native packaging.

## Defect and regression evidence

Hosted and manual validation identified and resolved:

1. OpenSpec change structure lacked a capability specification;
2. new Python files exceeded the repository line-length policy;
3. direct SQLite position swaps collided with the unique watchlist-position constraint;
4. the D4 navigation rewrite removed the established no-profile guidance from D3;
5. desktop profile ownership initially existed only inside short-lived Python sidecar processes, allowing a second window/process to bypass lifetime ownership;
6. supported direct Python/CLI mutations needed to coordinate with the desktop lifetime profile lease;
7. the first packaged macOS application depended on a repository/system Python environment instead of bundling its desktop service;
8. PyInstaller one-file packaging caused repeated 10–20 second sidecar/request delays;
9. the initial packaged-sidecar smoke used a 5-second subprocess budget inconsistent with the broker's 15-second request timeout;
10. the canonical macOS build attempted unrelated DMG creation and could fail after the application bundle itself was valid.

The final implementation uses a two-phase temporary-position transaction for reorder operations, preserves the D3 profile-state disclosure, coordinates desktop lifetime profile leases with supported external mutations, bundles a self-contained PyInstaller one-directory runtime, avoids repeated one-file extraction, and builds the native `.app` directly for macOS acceptance.

## macOS ARM64 manual acceptance

**Result: PASS.**

The complete D4 macOS acceptance was executed in five batches. Accepted evidence includes deterministic Markets behavior, persistence, locking and ownership, supported external mutation coordination, separate-profile isolation, no-network checks, accessibility/responsive behavior, direct packaged-app launch, packaged persistence/ownership, and the successful performance retest after the sidecar redesign.

## Linux x86-64 manual acceptance

**Result: PASS.**

The complete clean-profile D4 procedure also passed on Linux x86-64, including catalog/search ambiguity behavior, details and recents, watchlist lifecycle and restart persistence, same-profile ownership rejection, supported external mutation coordination, separate-profile isolation, offline/network boundaries, keyboard/Orca/high-contrast/reduced-motion/responsive behavior, native package build and packaged-application smoke, and packaged responsiveness.

Private host paths and machine-local profile identifiers are intentionally not committed.

## Current disposition

- Implementation slices: complete.
- Automated validation: pass on implementation candidate `08b1c00e32440022d57e7c659625bf7eac490bd8`.
- Security and narrow-authority checks: pass.
- macOS ARM64 manual acceptance: pass.
- Linux x86-64 manual acceptance: pass.
- D4 exit decision: pass; merge authorized by the repository owner, subject only to final CI on the evidence-reconciliation head.
