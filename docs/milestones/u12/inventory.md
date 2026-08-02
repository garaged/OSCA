# U12 Lifecycle Inventory

## Packaging

- `pyproject.toml` is the canonical package authority.
- Hatchling builds a pure-Python wheel and source distribution.
- Python support is constrained to 3.13.
- `uv` required environments declare Linux x86-64 and macOS arm64.
- The installed console surfaces are `osca` and the compatibility entry point `osca-research-pipeline`.

## Version and provenance

- Package version is currently `0.1.0.dev0`.
- `osca version` reports package, runtime, platform, build source, build commit, and safety state.
- `scripts/build_release_artifacts.py` emits SHA-256 checksums, a CycloneDX JSON SBOM, and versioned provenance.

## Profile and storage

- `osca init` creates strict versioned operator configuration.
- The configured storage root contains SQLite metadata, Parquet payloads, acquisition evidence, research evidence, and workspace artifacts.
- Unknown or unsafe configuration fields fail validation.

## Lifecycle protection

- `osca lifecycle inspect` checks platform, Python, configuration, and storage without mutation.
- `osca lifecycle backup` creates a manifest-backed ZIP and verifies every retained digest.
- `osca lifecycle restore` rejects undeclared or unsafe members and uses staged atomic replacement.
- `osca lifecycle upgrade` requires a verified backup and restores it automatically when mutation or post-upgrade validation fails.

## Existing migration authority

- Alembic and repository migration tests remain the database-schema authority.
- U12 does not invent a second migration engine; lifecycle orchestration protects the profile before approved migrations run.

## Deployment

- The workspace remains loopback-only and read-only by default.
- Personal-server use remains an explicit operator deployment with no remote write surface.
- Packaged startup uses the installed `osca workspace` command rather than a repository module invocation.
