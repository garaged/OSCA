# D1: Desktop architecture and application API foundation

- **Status:** Complete; deferred Linux hosted validation fulfilled during D2
- **Baseline:** U14 main at `85c332c8d3c1019ac0564c6e0ddb814feac5463a`
- **Branch:** `agent/d1-desktop-foundation`
- **Authority:** ADR-0046, `docs/product/desktop-product-intent.md`, `docs/roadmaps/desktop-product-roadmap.md`, `docs/product/cross-cutting-requirements.md`, `docs/product/desktop-capability-map.md`, and `docs/product/desktop-traceability.md`

D1 is the only milestone in PR #78 specified at implementation level. D2-D19 are represented by accepted, intentionally solution-light intent documents and receive executable specifications when their implementation begins.

## User-visible outcome

A developer-preview desktop application can open a new or existing OSCA profile and display application version, profile compatibility, storage health, Python-sidecar health, and recovery state without requiring terminal interaction.

## Scope

D1 will:

1. Establish a Tauri v2, React, and TypeScript desktop workspace.
2. Add a deliberately small Rust host broker.
3. Package and supervise the existing Python core as a local sidecar.
4. Define versioned command, query, error, and progress-event contracts.
5. Add profile locking, compatibility negotiation, cancellation, restart, and graceful shutdown.
6. Expose desktop-safe health, version, profile-inspection, and storage-diagnostic capabilities.
7. Add frontend, Rust, IPC, packaging, and architecture checks to Quality.
8. Produce a canonical capability map and identify command-oriented or duplicated surfaces that later milestones must consolidate.
9. Preserve CLI, analyst-workspace, release, provider, evidence, extension, and safety compatibility.

## Non-goals

D1 does not implement complete onboarding, provider credential setup, production charting, recommendations, virtual portfolios or simulated orders, expanded ML execution, AI-provider execution, Windows product support, broker or exchange connectivity, or real-money data, balances, orders, or execution.

## Architecture boundaries

- Python remains the deterministic analytical and domain authority.
- The frontend performs presentation and interaction only.
- The frontend cannot access SQLite, Parquet storage, secrets, arbitrary files, the shell, or extension executables directly.
- Rust exposes only allowlisted desktop capabilities and sidecar lifecycle operations.
- Desktop IPC must be local, versioned, schema-validated, bounded, cancellable, and incapable of invoking arbitrary CLI commands.
- The initial transport avoids opening a network listener; framed standard input/output is preferred unless D1 evidence proves a better local-only mechanism.
- Existing profile data must remain readable without destructive migration.

## Offline behavior

All D1 functionality must work with networking disabled. No provider, AI service, telemetry endpoint, or account is required.

## Security and privacy

- Network access remains opt-in.
- Telemetry remains disabled by default.
- No secret values cross desktop IPC during D1.
- Tauri capabilities and CSP must be minimal and tested.
- No arbitrary shell or generic command-execution capability may be exposed.
- ADR-0044 remains binding.

## ML, recommendations, and simulation

D1 may expose read-only health summaries for retained evidence, but it must not enable model promotion, recommendation generation, portfolio mutation, simulated ordering, or live execution.

## Required tests

- Python application-contract unit tests.
- IPC schema and compatibility tests.
- Malformed, oversized, unknown-version, and unknown-command handling.
- Sidecar startup, shutdown, crash, restart, cancellation, and orphan recovery.
- Profile-lock and incompatible-profile behavior.
- Frontend TypeScript and component tests.
- Rust formatting, lint, and unit tests.
- Architecture tests preventing frontend numerical authority and generic command execution.
- macOS ARM64 and Linux x86-64 development-package smoke tests.
- Existing Python, OpenSpec, extension, lifecycle, and release gates remain passing.

## Manual acceptance

On a clean supported machine:

1. Install the D1 development package.
2. Launch without a terminal.
3. Create or select an OSCA profile.
4. Confirm application, Python, contract, and profile versions are visible.
5. Confirm storage and profile diagnostics are actionable.
6. Stop the sidecar and confirm the application explains and recovers from the failure.
7. Close and reopen the application without profile corruption or orphan processes.
8. Confirm the existing CLI can still inspect the same profile.
9. Confirm no network access occurs during the workflow.

## Migration requirements

- U14 profiles open without destructive migration.
- Any desktop-specific state is isolated from analytical evidence.
- A future migration path is versioned from the first persisted desktop schema.
- Failed initialization leaves the profile unchanged.

## Documentation

D1 must update architecture status, decision index, desktop developer bootstrap, desktop application contract reference, manual testing, contributor workflow, risk and limitation records, OpenSpec, traceability, and the D2-D19 intent baseline.

## Exit criteria

D1 is complete only when:

- the developer-preview desktop package launches on macOS ARM64 and Linux x86-64;
- the supervised Python sidecar and IPC contract pass failure and compatibility tests;
- the application opens an existing U14 profile safely;
- Quality contains desktop-specific gates without weakening existing gates;
- the capability map and consolidation plan are retained;
- manual acceptance passes on both supported platforms;
- no untreated critical security, migration, packaging, accessibility, or safety risk remains.

## Accepted validation evidence

The project owner accepted the following local D1 evidence on 2026-08-05:

- Ruff passed.
- Strict mypy passed across the Python source tree.
- Pytest passed with 442 tests and one non-blocking warning.
- OpenSpec doctor and strict validation passed.
- Trusted-local extension conformance passed.
- Desktop React and TypeScript checks and production build passed.
- Rust formatting, Clippy with warnings denied, tests, and checks passed.
- Tauri development launch and macOS ARM64 production build passed.
- Python wheel and source distribution build, lifecycle exercise, checksums, SBOM, and provenance generation passed locally.
- Manual macOS ARM64 validation confirmed sidecar health, disabled live execution, clean shutdown, restart behavior, and no orphan sidecar.
- Missing protocol typing, lint compatibility, desktop dependency lockfile, and Tauri icon assets found during validation were corrected and committed.

## Hosted-validation follow-up

GitHub-hosted Actions could not execute the final D1 checks at D1 closeout because the account's monthly Actions allowance was exhausted. The owner accepted that as a temporary infrastructure exception, with Linux x86-64 package and launch evidence explicitly deferred to D2.

That deferred obligation is now fulfilled:

- Desktop Foundation run `31065065075` built the Debian desktop package, launched the packaged binary in a bounded Xvfb smoke, inspected the package, and uploaded the retained artifact from commit `112726750c6a1bd060ddc29dc840af83dbd68480`.
- Desktop Foundation run `31065891295` repeated the Linux package build, launch smoke, package inspection, and artifact upload after D2 hardening on commit `3e5837fe30a56573bf45cc1fdcee4ac3c7f97f98`.
- Retained artifact `8953859616`, `osca-d1-d2-linux-desktop-package`, has digest `sha256:c7f4e5377e522fb1cdcea93aad11ecef7f0f0a6d801ff8179fcdddd8bbb1d43f` and an expiry date of 2026-11-04.
- The full macOS ARM64 local gate remains the accepted D1 macOS evidence.

Disposition: the D1 hosted-validation exception is closed. Future ready-for-review and release-candidate workflows still rerun current Linux package smoke and the normal Linux/macOS contributor and package-lifecycle matrices; those are ongoing release gates rather than unresolved D1 debt.

## Dependencies

D1 depends only on the completed U14 baseline and accepted ADR-0046.

## Principal risks

Python runtime and sidecar packaging complexity, system-WebView differences, excessive Rust-domain growth, accidental CLI coupling, IPC version drift, desktop packaging destabilizing the Python distribution, and premature UI work before application-service boundaries are stable.

## Product decision status

No additional product decision is required before D1 implementation. Tauri is approved as the primary direction, with Electron retained only as an evidence-triggered fallback if D1 exit criteria cannot be met.
