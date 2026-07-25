# M5 Scope

- **Status:** Active
- **Baseline:** Completed M4

## In scope

- Extension package manifest contracts.
- Extension categories, entry points, compatibility ranges, schemas, intervals, asset classes, dependencies, permissions, resource limits, determinism, and provenance metadata.
- Trust tiers and activation states.
- Install records with exact package identity, version, source, digest, dependencies, permissions, and activation state.
- Activation decisions that fail closed for untrusted/quarantined packages or changed permissions.
- Disable and uninstall impact previews against retained artifact references.
- Additive application services and unit tests.

## Out of scope

- Runtime isolation implementation.
- Dynamic import or execution of third-party Python.
- Public registry, publisher onboarding, or certificate infrastructure.
- UI and CLI administration flows beyond contract/service readiness.
- Strategy, backtesting, ML, LLM, paper trading, and live execution.
