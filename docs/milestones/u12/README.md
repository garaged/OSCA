# U12 — Packaging, Upgrade, Backup, and Rollback

- **Status:** Implementation and hosted platform conformance complete; clean-machine acceptance pending
- **Baseline:** U11 merged through PR #74 at `1e46d92c37db92fcc30a41fcc7ff18df8aa23f42`
- **Branch:** `agent/u12-packaging-upgrade-rollback`
- **Implementation PR:** #75

## Intent

Create a repeatable supported installation and lifecycle experience for OSCA on macOS Apple Silicon and Linux x86-64 without weakening U11 safe defaults or losing accepted evidence.

## Delivered outcome

1. Pure-Python wheel and source distribution build through the canonical package metadata.
2. Isolated installation with `uv tool install` and no runtime repository checkout.
3. `osca version` package/runtime/platform/build reporting.
4. SHA-256 checksum manifest, CycloneDX JSON SBOM, and versioned build provenance.
5. Hosted package lifecycle validation on macOS arm64 and Linux x86-64.
6. Non-mutating `osca lifecycle inspect` compatibility checks.
7. Digest-verified full-profile backup before mutation.
8. Safe restore with manifest validation, path containment, staging, and atomic replacement.
9. Upgrade orchestration that requires a verified backup and automatically recovers after mutation or validation failure.
10. Automated evidence-digest preservation checks.

## Operator lifecycle

```text
osca version
osca lifecycle inspect --profile-root PROFILE
osca lifecycle backup --profile-root PROFILE --output BACKUP.zip
osca lifecycle upgrade --profile-root PROFILE --backup BACKUP.zip --target-version VERSION
osca lifecycle restore --backup BACKUP.zip --profile-root RESTORED_PROFILE
```

The packaged workspace starts through:

```text
osca workspace --profile-root PROFILE
```

It remains loopback-only and read-only by default.

## Validation

Quality run #753 passed the macOS arm64 and Linux x86-64 package lifecycle jobs, plus Ruff, strict mypy, the complete test/contract/migration/link/architecture suite, OpenSpec strict validation, and secret scanning.

## Remaining gate

Run [U12 clean-machine acceptance](manual-acceptance.md) independently on both supported platforms and retain the full workflow, successful upgrade, failed-upgrade recovery, restore, rollback, workspace, and evidence-preservation outputs.

## Safety boundaries

U12 does not enable recommendations, automatic promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication. Lifecycle operations preserve accepted evidence and fail closed before destructive mutation.

## Next milestone

U13 owns release-candidate versioning, official acceptance-matrix execution, defect threshold, release notes, and tag authority.
