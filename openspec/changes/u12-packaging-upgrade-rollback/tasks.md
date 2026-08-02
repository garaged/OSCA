# Tasks: U12 Packaging, Upgrade, Backup, and Rollback

## Specification and inventory

- [x] Record U12 intent, non-goals, supported platforms, exit gate, and safety boundaries.
- [ ] Inventory current package metadata, versioning, migration, backup/restore, and deployment surfaces.
- [ ] Define lifecycle evidence contracts and compatibility policy.

## Packaging and provenance

- [ ] Establish the supported isolated installation path.
- [ ] Add canonical version/build/provenance reporting.
- [ ] Produce deterministic package checksums.
- [ ] Produce an SBOM for release artifacts.
- [ ] Retain build provenance and supported-platform metadata.
- [ ] Add macOS Apple Silicon and Linux x86-64 installation validation.

## Upgrade and recovery

- [ ] Add configuration/storage compatibility inspection.
- [ ] Require backup-before-migration.
- [ ] Add explicit restore validation.
- [ ] Add failed-upgrade recovery behavior.
- [ ] Add rollback rehearsal and evidence comparison.
- [ ] Prove accepted evidence survives the complete lifecycle.

## Documentation and acceptance

- [ ] Document packaged workspace startup.
- [ ] Reconcile personal-server deployment guidance.
- [ ] Reconcile root README and central manual testing.
- [ ] Add U12 traceability, manual acceptance, and exit review.
- [ ] Pass hosted Quality and platform lifecycle jobs.
- [ ] Retain clean-machine acceptance evidence for both supported platforms.
