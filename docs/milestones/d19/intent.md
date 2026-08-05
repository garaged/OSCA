# D19 Intent — Desktop Release Candidate and Broadly Usable Release Acceptance

## Outcome
OSCA ships as a signed, recoverable, broadly usable desktop research product whose supported workflows, safety boundaries, platform behavior, migrations, and limitations are proven through retained release evidence.

## Scope
Contract and profile freeze, signed installers, update channels, backup and restore, migration rehearsal, full automated and manual platform matrix, release notes, support bundle, SBOM and provenance, rollback and recovery, clean-profile acceptance, and final architecture reconciliation.

## Non-goals
Last-minute feature expansion, live trading, unsupported providers, hidden experimental capability, or bypassing failed acceptance gates.

## Dependencies
D18 completion and first-class macOS ARM64, Linux x86-64, and Windows x86-64 support.

## Risks
Packaging drift, signing or updater failures, migration damage, incomplete platform parity, unclear support boundaries, and pressure to waive defects.

## Exit intent
`1.0.0rc1` is produced only after all release gates pass. Acceptance proves installation, update, migration, backup/restore, offline use, governed providers, analysis, backtesting, ML, recommendations, simulation, reporting, extensions, accessibility, diagnostics, and explicit absence of any live-order path. The polished accepted release becomes `1.0.0`.
