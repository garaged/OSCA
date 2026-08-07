# D4 Validation Evidence — Asset Catalog, Market Browser, and Watchlists

- **Status:** Automated validation passed; supported-platform manual acceptance pending
- **Pull request:** #84
- **Branch:** `agent/d4-asset-catalog-watchlists`
- **Baseline:** D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`
- **Validated implementation candidate:** `2675816dd0d128009c74ccbb009628677c2cb3b4`

## Automated validation

The implementation candidate passed:

- Quality run `31140148497`;
- Desktop Foundation run `31140148520`;
- strict OpenSpec validation;
- secret scanning;
- Ruff and strict mypy;
- the full Python, contract, migration, link, and architecture suite;
- desktop API and launcher tests;
- frontend TypeScript build and Node test suite;
- Rust formatting, unit tests, and Clippy.

The suite contains focused D4 coverage for deterministic asset search, provider aliases, exact-symbol ambiguity, canonical identifiers, profile-scoped SQLite persistence, ordered watchlist membership, collision-safe reorder, typed offline desktop methods, narrow frontend authority, responsive layout, reduced motion, and forced-colors safeguards.

## Defect and regression evidence

Hosted validation identified and resolved:

1. OpenSpec change structure lacked a capability specification;
2. new Python files exceeded the repository line-length policy;
3. direct SQLite position swaps collided with the unique watchlist-position constraint;
4. the D4 navigation rewrite removed the established no-profile guidance from D3.

The final implementation uses a two-phase temporary-position transaction for reorder operations and preserves the D3 profile-state disclosure across Markets and Data Sources.

## Remaining evidence

The complete clean-profile procedure in `manual-acceptance.md` must pass on:

- macOS ARM64;
- Linux x86-64.

That evidence must include accessibility, network observation, restart persistence, concurrent profile locking, native package build, and packaged-application smoke. Machine-local evidence should remain outside the repository when it contains host-specific paths or private data.

## Current disposition

- Implementation slices: complete.
- Automated validation: pass.
- Security and narrow-authority checks: pass.
- Supported-platform manual acceptance: pending.
- D4 exit decision: pending manual evidence and explicit repository-owner direction.
