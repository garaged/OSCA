# Tasks: U12 Packaging, Upgrade, Backup, and Rollback

## Specification and inventory

- [x] Record U12 intent, non-goals, supported platforms, exit gate, and safety boundaries.
- [x] Inventory current package metadata, versioning, migration, backup/restore, and deployment surfaces.
- [x] Define lifecycle evidence contracts and compatibility policy.

## Packaging and provenance

- [x] Establish the supported isolated installation path.
- [x] Add canonical version/build/provenance reporting.
- [x] Produce deterministic package checksums.
- [x] Produce an SBOM for release artifacts.
- [x] Retain build provenance and supported-platform metadata.
- [x] Add macOS Apple Silicon and Linux x86-64 installation validation.

## Upgrade and recovery

- [x] Add configuration/storage compatibility inspection.
- [x] Require backup-before-migration.
- [x] Add explicit restore validation.
- [x] Add failed-upgrade recovery behavior.
- [x] Add rollback rehearsal and evidence comparison.
- [x] Prove accepted evidence survives the automated lifecycle.

## Documentation and acceptance

- [x] Document packaged workspace startup.
- [x] Reconcile personal-server deployment guidance through loopback-only packaged startup.
- [ ] Reconcile root README and central manual testing.
- [x] Add U12 traceability, manual acceptance, and exit review.
- [x] Pass hosted Quality and platform lifecycle jobs.
- [ ] Retain clean-machine acceptance evidence for both supported platforms.
