# U12 Traceability

| Requirement | Implementation | Validation |
|---|---|---|
| Isolated supported install | wheel build and `uv tool install` in Quality matrix | `package-lifecycle` jobs on macOS arm64 and Linux x86-64 |
| Version/build identity | `osca version`, `version_report` | U12 unit tests and packaged CLI run |
| Checksums | `scripts/build_release_artifacts.py`, `SHA256SUMS` | platform jobs independently recompute SHA-256 |
| SBOM | CycloneDX JSON artifact | artifact generation on both platforms |
| Provenance | `osca.release-provenance` JSON | source commit/repository and artifact digests retained |
| Compatibility before mutation | `osca lifecycle inspect` | compatible and fail-closed profile tests |
| Backup before migration | `create_verified_backup`, `osca lifecycle upgrade` | upgrade tests require verified backup first |
| Safe restore | manifest/digest validation, path containment, staged atomic swap | overwrite refusal, traversal rejection, restore tests |
| Failed-upgrade recovery | automatic restore from pre-upgrade backup | simulated corruption/deletion recovery tests |
| Evidence preservation | before/after profile digest comparison | recovery tests and clean-machine acceptance |
| Supported platforms | `.github/workflows/quality.yml` matrix | `macos-14` arm64 and `ubuntu-24.04` x86-64 |
| Safety boundaries | all lifecycle result contracts keep unsafe capabilities false | unit tests, packaged version output, manual acceptance |
