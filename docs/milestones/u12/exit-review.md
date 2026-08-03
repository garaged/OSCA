# U12 Exit Review

- **Milestone:** U12 packaging, upgrade, backup, and rollback
- **Status:** Complete
- **Implementation PR:** #75
- **Accepted clean-machine evidence:** GitHub-hosted ephemeral macOS Apple Silicon and Linux x86-64 runners

## Delivered outcome

U12 provides a supported wheel-based lifecycle with isolated `uv tool` installation, package/runtime/platform reporting, checksums, CycloneDX SBOM, provenance, compatibility inspection, verified backup, safe restore, mandatory backup-before-upgrade, and automatic failed-upgrade recovery.

## Accepted evidence

The project accepts fresh GitHub-hosted ephemeral runners as the clean-machine platform evidence for U12. Quality run #760 validated both supported platforms from source artifact creation through installed CLI use:

- wheel and source distribution build;
- SHA-256 manifest generation and independent verification;
- CycloneDX SBOM and versioned provenance generation;
- isolated wheel installation with `uv tool install`;
- packaged `osca version`, initialization, inspection, backup, restore, and reinspection;
- macOS Apple Silicon execution on a fresh `macos-14` arm64 runner;
- Linux x86-64 execution on a fresh `ubuntu-24.04` runner;
- Ruff, strict mypy, complete tests/contracts/migrations/links/architecture;
- OpenSpec strict validation and secret scanning.

Unit coverage also proves incompatible-profile refusal, manifest and digest verification, ZIP path-containment enforcement, explicit overwrite consent, staged atomic restore, mandatory pre-upgrade backup, simulated mutation failure, automatic recovery, and pre-upgrade digest preservation.

## Acceptance checklist

- [x] Supported isolated package installation path exists.
- [x] Canonical version/build reporting exists.
- [x] Checksums, SBOM, and provenance are generated.
- [x] macOS arm64 packaged lifecycle job passes on a fresh ephemeral runner.
- [x] Linux x86-64 packaged lifecycle job passes on a fresh ephemeral runner.
- [x] Compatibility inspection is non-mutating and fail-closed.
- [x] Backup is verified before lifecycle mutation.
- [x] Restore rejects unsafe or inconsistent archives.
- [x] Failed upgrades automatically recover from the verified backup.
- [x] Automated evidence preservation is covered.
- [x] Clean-machine evidence is retained for macOS arm64.
- [x] Clean-machine evidence is retained for Linux x86-64.

## Residual limitations

- The repository remains at development version `0.1.0.dev0`; U13 owns release-candidate version/tag authority.
- Release signing and publication are not performed in U12.
- No no-cost equity provider has been admitted; governed CSV/Parquet import remains the equity fallback.

## Exit decision

U12 is complete. The hosted ephemeral platform jobs satisfy the clean-machine requirement, all lifecycle and safety gates pass, and U13 is the next milestone.
