# U12 — Packaging, Upgrade, Backup, and Rollback

- **Status:** Complete
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
5. Hosted package lifecycle validation on fresh macOS arm64 and Linux x86-64 runners.
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

Quality run #760 passed the complete hosted suite. The project accepts fresh GitHub-hosted ephemeral runners as U12 clean-machine evidence:

- macOS Apple Silicon: fresh `macos-14` arm64 runner;
- Linux x86-64: fresh `ubuntu-24.04` runner;
- wheel and source distribution build;
- checksums, CycloneDX SBOM, and provenance generation;
- isolated `uv tool` installation;
- packaged init, inspect, backup, restore, and reinspection;
- Ruff, strict mypy, complete tests/contracts/migrations/links/architecture;
- OpenSpec strict validation and secret scanning.

## Safety boundaries

U12 does not enable recommendations, automatic promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication. Lifecycle operations preserve accepted evidence and fail closed before destructive mutation.

## Next milestone

U13 owns release-candidate versioning, official acceptance-matrix execution, defect threshold, release notes, and tag authority.
