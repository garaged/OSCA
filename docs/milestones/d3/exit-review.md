# D3 Exit Review — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Pending refreshed hosted validation
- **Review date:** 2026-08-06 (America/Mexico_City)
- **Pull request:** #83
- **Accepted baseline:** D2 merge `7522da7bc50fa1fdffa4088c0f39f5d2ebe7d9b6`
- **Decision:** Manual and product gates pass; final merge readiness awaits refreshed hosted validation and explicit owner direction.

## Review scope

This review evaluates whether D3 delivered an honest, local-first data-source workspace while preserving Python authority, secure credential handling, explicit request-scoped networking, free/offline functionality, canonical evidence, and the permanent no-live-execution boundary.

## Delivered outcome

D3 provides:

- a first-class Data Sources desktop area;
- provider policy and resource-admission visibility independent from credential state;
- OS-vault credential store, replace, probe, and delete operations with no secret return path;
- governed local OHLCV CSV import and bundled synthetic data as universal no-cost paths;
- approved no-key Kraken public spot OHLC acquisition with explicit consent for each request;
- synchronous request semantics without fake live progress or cross-request cancellation claims;
- canonical acquisition reuse, retained evidence, restart recovery, and profile-root scoping;
- typed invalid, provider, quota, network, corrupt, stale, partial, cancelled, and failed outcomes;
- responsive, keyboard-accessible, screen-reader-compatible desktop presentation;
- a reusable Makefile for setup, validation, isolated acceptance, launch, build, package, test, lint, type checking, formatting, status, and cleanup;
- no recommendation generation, broker/exchange connection, autonomous execution, live order, or real-capital path.

## Specification and traceability review

- Requirements `REQ-0294` through `REQ-0308` are allocated and implemented.
- The D3 intent, specification, requirements catalog, OpenSpec change, traceability record, manual-acceptance procedure, and implementation agree on scope and boundaries.
- Provider admission remains policy-derived and is not promoted by credential presence.
- Offline and free paths remain available without a provider account.
- React and Rust retain only the narrow `desktop_request` bridge and gain no generic filesystem, keychain, HTTP, shell, or database authority.

Disposition: pass.

## Manual, accessibility, and packaged-app review

The repository owner reported the complete D3 manual-acceptance procedure passed on:

- macOS ARM64, including VoiceOver and packaged-app smoke;
- Linux x86-64, including Orca and packaged-app smoke.

Accepted coverage included clean onboarding, profile lifecycle, provider policy, credential redaction, valid/repeated/malformed import, explicit Kraken consent, acquisition reuse, retained evidence, restart persistence, network observation, failure recovery, lock contention, concurrent mutation protection, responsive layouts, appearance/contrast, reduced motion, and native package operation.

Machine-local evidence remains outside the repository to avoid exposing host-specific paths or private data.

Disposition: pass.

## Security and safety review

- Credential values are sent only to the Python service for OS-vault storage and are never returned to React.
- Credential presence does not alter provider admission.
- Offline import and catalog/credential operations do not produce unexpected external provider traffic.
- Kraken traffic requires explicit one-request consent and no API key.
- Retained evidence remains canonical and profile-scoped.
- Recommendation and execution capabilities remain disabled.
- Hosted secret scanning passed on earlier D3 candidates and must pass again on the final reconciled head.

Disposition: pass, subject to refreshed hosted confirmation.

## Defect disposition

Manual acceptance found and resolved:

- Vite test-server collision and false error noise;
- header mode-switch overlap;
- invisible consent checkbox on macOS;
- `acquisition.submit` versus `acquisition.run` method drift;
- acquisition-result envelope parsing drift;
- retained-list field-name drift.

Refreshed hosted validation then found and resolved:

- Makefile-test import ordering rejected by Ruff;
- brittle frontend source-contract assertions.

Release-blocking product defects: none known after fixes.

## Automated validation review

Earlier ready-state hosted runs passed, including Quality `31100587952`, Desktop Foundation `31100587598`, both supported contributor/package matrices, secret scanning, Rust validation, and Linux packaged-binary smoke.

The first refreshed run after manual fixes failed because of the two test-quality defects listed above, not because of a runtime product failure. Those defects are corrected. Final automated disposition remains pending until the next hosted runs complete successfully on the reconciled head.

## Non-blocking follow-ups

- Continue improving typed frontend contract tests toward executable fixtures rather than source-text assertions.
- Consider upgrading GitHub Actions versions that still emit Node.js runtime deprecation warnings.
- Carry the accepted Data Sources surface into later research and visualization milestones without broadening native authority.

These follow-ups do not invalidate D3 behavior or accepted manual evidence.

## Exit decision

D3 satisfies its intent, requirements, implementation, supported-platform manual acceptance, accessibility, security, data-integrity, network-consent, free/offline-path, packaged-app, traceability, and evidence obligations. Final PR merge readiness is conditional on refreshed hosted validation passing. The merge itself remains gated on explicit repository-owner direction.
