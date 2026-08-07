# D3 Exit Review — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Passed
- **Review date:** 2026-08-06 (America/Mexico_City)
- **Pull request:** #83
- **Accepted baseline:** D2 merge `7522da7bc50fa1fdffa4088c0f39f5d2ebe7d9b6`
- **Decision:** D3 satisfies its exit criteria and is ready for explicit owner-directed merge.

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

- Requirements `REQ-0294` through `REQ-0308` are allocated, implemented, and verified.
- The D3 intent, specification, requirements catalog, OpenSpec change, traceability record, manual-acceptance procedure, implementation, and evidence agree on scope and boundaries.
- Provider admission remains policy-derived and is not promoted by credential presence.
- Offline and free paths remain available without a provider account.
- React and Rust retain only the narrow `desktop_request` bridge and gain no generic filesystem, keychain, HTTP, shell, or database authority.

Disposition: pass.

## Manual, accessibility, and packaged-app review

The complete D3 manual-acceptance procedure passed on:

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
- Hosted secret scanning passed on the final validated candidate.

Disposition: pass.

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
- brittle frontend source-contract assertions;
- stale consent-control id assertion.

Release-blocking product defects: none known after fixes.

## Automated validation review

The final reconciled candidate at `814c33090eac57323eeccf66e9bd75be35c62d98` passed:

- Quality run `31136335873`;
- Desktop Foundation run `31136335867`;
- both supported contributor/package matrices;
- secret scanning, OpenSpec, Python, frontend, Rust, architecture validation, and Linux packaged-binary smoke.

Disposition: pass.

## Non-blocking follow-ups

- Continue improving typed frontend contract tests toward executable fixtures rather than source-text assertions.
- Consider upgrading GitHub Actions versions that still emit Node.js runtime deprecation warnings.
- Carry the accepted Data Sources surface into later research and visualization milestones without broadening native authority.

These follow-ups do not invalidate D3 behavior or accepted evidence.

## Exit decision

D3 satisfies its intent, requirements, implementation, supported-platform manual acceptance, accessibility, security, data-integrity, network-consent, free/offline-path, packaged-app, traceability, hosted validation, and evidence obligations. The milestone is ready to merge. The merge itself remains gated on explicit repository-owner direction.
