# Change: U12 Packaging, Upgrade, Backup, and Rollback

## Why

U11 provides a complete primary operator workflow from a source checkout, but OSCA still lacks an evidenced clean-machine installation and lifecycle path. A usable release candidate requires repeatable installation, explicit compatibility checks, backup-before-migration, failed-upgrade recovery, and rollback without loss of accepted evidence.

## What changes

- establish a supported isolated installation path for macOS Apple Silicon and Linux x86-64;
- expose version, build, and provenance information through the primary CLI;
- define configuration and storage compatibility inspection before mutation;
- require a verified backup before any migration that may alter retained state;
- add explicit restore, failed-upgrade recovery, and rollback workflows;
- generate checksums, SBOM, and provenance evidence for packaged artifacts;
- validate packaged workspace startup and personal-server deployment guidance;
- add clean-machine lifecycle acceptance and hosted platform coverage.

## Non-goals

- publishing a stable public release or release candidate tag, which belongs to U13;
- enabling recommendations, model promotion, brokers, autonomous execution, or real-capital orders;
- introducing a graphical installer;
- supporting additional operating systems or architectures in U12;
- silently migrating or deleting incompatible evidence.

## Exit gate

Fresh install, workflow execution, upgrade, backup/restore, failed-upgrade recovery, and rollback pass on macOS Apple Silicon and Linux x86-64 without loss of accepted evidence.
