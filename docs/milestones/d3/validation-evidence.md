# D3 Validation Evidence — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Manual validation passed; refreshed hosted validation pending
- **Validation date:** 2026-08-06 (America/Mexico_City)
- **Pull request:** #83
- **Branch:** `agent/d3-provider-onboarding`
- **D2 baseline:** `7522da7bc50fa1fdffa4088c0f39f5d2ebe7d9b6`

## Automated validation

The earlier D3 ready-state candidate passed:

- Quality run `31100587952`;
- Desktop Foundation run `31100587598`;
- Linux x86-64 and macOS ARM64 contributor rehearsals;
- Linux x86-64 and macOS ARM64 package-lifecycle matrices;
- frontend build/tests, Python desktop boundary, Rust format/unit/Clippy, OpenSpec, architecture checks, and secret scanning;
- Linux Debian package build and packaged-binary smoke;
- Linux artifact `8967388408`, digest `sha256:1c12623fe106067128611e017f1c6d5e732f8d31f7fbca741c7867525558dd75`.

Manual acceptance subsequently found integration and presentation defects. Those defects were fixed and regression checks were added. Refreshed hosted validation for the final reconciled head must pass before this document is promoted to final accepted evidence.

## Manual validation

The repository owner reported all six acceptance batches passed on macOS ARM64 and Linux x86-64.

Accepted coverage included:

- clean first run, permanent disclosures, keyboard navigation, focus, and responsive mode-switch layout;
- profile inspection, creation, opening, restart persistence, diagnostics, and local synthetic data;
- provider catalog policy, credential lifecycle, redaction, and proof that credential presence does not promote admission;
- governed valid, repeated, missing, malformed, and unsafe local CSV import behavior;
- request-scoped Kraken acquisition with explicit one-request consent and no API key;
- canonical reuse, retained evidence, restart persistence, and profile-root scoping;
- network observation proving offline actions did not produce unexpected provider traffic;
- provider/network failure handling, retry behavior, consent reset, and honest failed evidence;
- profile-lock contention, concurrent mutation protection, restart recovery, and continued operation;
- light/dark/high-contrast, reduced-motion, VoiceOver, Orca, narrow/intermediate/desktop layouts;
- native package build and packaged-application smoke on both supported platforms;
- continued absence of recommendations, broker/exchange connectivity, autonomous execution, live orders, and real-capital execution.

## Defect and regression evidence

Acceptance discovered and resolved:

1. nondeterministic Vite test-server port collision and shutdown noise;
2. header mode-switch overlap with safety badges;
3. effectively invisible Kraken consent checkbox on macOS;
4. frontend/Python method drift between `acquisition.submit` and `acquisition.run`;
5. acquisition-result `evidence` envelope parsing drift;
6. retained-list `evidence` versus `acquisitions` field drift;
7. hosted lint failure caused by Makefile-test import ordering;
8. brittle frontend source assertions around multiline parser formatting.

The final two items were found by refreshed hosted validation after manual acceptance and fixed before final reconciliation.

## Evidence handling

Machine-local evidence is intentionally not committed because it contains host-specific paths and environment details. The owner retained environment output, screenshots, accessibility notes, network observations, package output, profile/revision identifiers, and redacted credential metadata under the isolated acceptance evidence directories.

## Current disposition

- macOS ARM64 manual acceptance: pass.
- Linux x86-64 manual acceptance: pass.
- Security, accessibility, data-integrity, network-consent, recovery, and packaged-smoke manual gates: pass.
- Refreshed hosted validation on the reconciled final head: pending.
- Merge authorization: pending explicit repository-owner direction.
