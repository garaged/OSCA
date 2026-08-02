# U12 Exit Review

- **Milestone:** U12 packaging, upgrade, backup, and rollback
- **Status:** Automated conformance complete; clean-machine lifecycle acceptance pending
- **Implementation PR:** #75
- **Decision gate:** independent clean-machine evidence on macOS Apple Silicon and Linux x86-64

## Delivered outcome

U12 now provides a supported wheel-based lifecycle with isolated `uv tool` installation, package/runtime/platform reporting, checksums, CycloneDX SBOM, provenance, compatibility inspection, verified backup, safe restore, mandatory backup-before-upgrade, and automatic failed-upgrade recovery.

## Automated evidence

Quality run #753 validates both supported platforms from source artifact creation through installed CLI use:

- wheel and source distribution build;
- SHA-256 manifest generation and independent verification;
- CycloneDX SBOM and versioned provenance generation;
- isolated wheel installation with `uv tool install`;
- packaged `osca version`, initialization, inspection, backup, restore, and reinspection;
- Ruff, strict mypy, complete tests/contracts/migrations/links/architecture;
- OpenSpec strict validation and secret scanning.

Unit coverage also proves incompatible-profile refusal, manifest and digest verification, ZIP path-containment enforcement, explicit overwrite consent, staged atomic restore, mandatory pre-upgrade backup, simulated mutation failure, automatic recovery, and pre-upgrade digest preservation.

## Acceptance checklist

- [x] Supported isolated package installation path exists.
- [x] Canonical version/build reporting exists.
- [x] Checksums, SBOM, and provenance are generated.
- [x] macOS arm64 packaged lifecycle job passes.
- [x] Linux x86-64 packaged lifecycle job passes.
- [x] Compatibility inspection is non-mutating and fail-closed.
- [x] Backup is verified before lifecycle mutation.
- [x] Restore rejects unsafe or inconsistent archives.
- [x] Failed upgrades automatically recover from the verified backup.
- [x] Automated evidence preservation is covered.
- [ ] Independent clean-machine full workflow/upgrade/recovery/rollback evidence is retained for macOS arm64.
- [ ] Independent clean-machine full workflow/upgrade/recovery/rollback evidence is retained for Linux x86-64.

## Residual limitations

- The repository remains at development version `0.1.0.dev0`; U13 owns release-candidate version/tag authority.
- Release signing and publication are not performed in U12.
- Clean-machine acceptance requires two external platform executions even though hosted package lifecycle jobs are green.
- No no-cost equity provider has been admitted; governed CSV/Parquet import remains the equity fallback.

## Exit decision

Implementation and hosted supported-platform conformance are complete. U12 remains open only for the two clean-machine lifecycle evidence sets defined in `manual-acceptance.md`.
