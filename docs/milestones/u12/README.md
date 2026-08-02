# U12 — Packaging, Upgrade, Backup, and Rollback

- **Status:** In progress
- **Baseline:** U11 merged through PR #74 at `1e46d92c37db92fcc30a41fcc7ff18df8aa23f42`
- **Branch:** `agent/u12-packaging-upgrade-rollback`

## Intent

Create a repeatable supported installation and lifecycle experience for OSCA on macOS Apple Silicon and Linux x86-64 without weakening U11 safe defaults or losing accepted evidence.

## Exit outcome

Fresh installation, primary workflow execution, upgrade, backup-before-migration, failed-upgrade recovery, restore, and rollback are evidenced on both supported platforms.

## Scope

1. Supported isolated installation through `uv tool` or an equivalent reproducible path.
2. Package metadata and version reporting suitable for release-candidate rehearsal.
3. macOS Apple Silicon and Linux x86-64 build/install validation.
4. Checksums, SBOM, provenance, and changelog authority.
5. Configuration and storage compatibility inspection before mutation.
6. Backup-before-migration and explicit restore contracts.
7. Failed-upgrade recovery and rollback rehearsal.
8. Packaged workspace startup and personal-server deployment guidance.
9. Clean-machine lifecycle acceptance and retained evidence.

## Safety boundaries

U12 does not enable recommendations, automatic promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication. Lifecycle operations must preserve accepted evidence and fail closed before destructive mutation.

## Implementation sequence

1. Inventory packaging, versioning, migration, backup, and deployment surfaces.
2. Define OpenSpec lifecycle contracts and supported-platform matrix.
3. Add package/version/build provenance commands and artifacts.
4. Add compatibility inspection and backup-before-migration orchestration.
5. Add restore, failed-upgrade recovery, and rollback contracts.
6. Add CI platform installation/lifecycle jobs.
7. Reconcile README, manual testing, changelog, SBOM, and deployment guidance.
8. Run clean-machine lifecycle acceptance on both supported platforms.
