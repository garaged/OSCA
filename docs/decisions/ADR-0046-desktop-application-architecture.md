# ADR-0046: Desktop application architecture

- **Status:** Accepted
- **Date:** 2026-08-04
- **Owners:** Product authority, architecture authority, security authority
- **Related milestones:** D1-D19

## Context

OSCA has completed the U14 usable-release roadmap as a local-first Python research workbench. The current product has governed data, deterministic analysis, backtesting, retained evidence, local ML validation, lifecycle recovery, a read-only loopback workspace, and trusted-local extension foundations. Its primary usability gap is that most writable workflows remain command-oriented.

The next product phase must create a polished desktop application without duplicating numerical authority, weakening evidence retention, or adding any real-money execution capability.

## Decision

OSCA will use the following primary desktop architecture:

1. Tauri v2 desktop shell.
2. React and TypeScript frontend.
3. A narrow Rust host broker for desktop capabilities and Python-sidecar lifecycle.
4. The existing Python modular-monolith core as the deterministic application and domain authority.
5. Versioned, schema-validated local command, query, and event contracts between the host and Python core.
6. SQLite metadata and Parquet/artifact storage remain authoritative.

Electron is the evidence-triggered fallback only if D1 proves that Tauri cannot meet OSCA requirements for Python-sidecar packaging, chart compatibility, accessibility, security, or supported-platform distribution.

The frontend must not calculate authoritative indicators, portfolio values, fills, recommendations, risk decisions, or model eligibility. It must not parse CLI output, access SQLite directly, hold provider credentials, or execute extensions.

The Rust host must remain small. It may supervise the Python process, validate and frame IPC, bridge native file dialogs and credential stores, deliver desktop notifications, manage signed updates, and enforce profile/process lifecycle. Financial and analytical business logic remains in Python.

The desktop product targets macOS Apple Silicon and Linux x86-64 first. Windows x86-64 is required before the first polished desktop release and must receive its own packaging, signing, CI, migration, and clean-machine acceptance work.

## Accepted product decisions

- Recommendations launch as an explicit user-enabled research feature.
- Initial AI support uses user-managed local runtimes and optional cloud providers; no model is bundled initially.
- Development uses a `0.2.0` prerelease line and the complete desktop release candidate is `1.0.0rc1`.
- ADR-0044 remains binding. The desktop architecture must not add broker or exchange credentials, live-order adapters, real balances, real orders, autonomous execution, or any path that can move real funds.

## Consequences

- CLI, desktop, personal-server, and compatibility workspace adapters must converge on shared application services.
- The current server-rendered analyst workspace remains available during migration but does not become the desktop frontend.
- Long-running work uses durable typed jobs with progress, cancellation, recovery, and evidence.
- Desktop quality gates must cover TypeScript, Rust, IPC compatibility, packaging, accessibility, visual regression, signing, updates, and supported platforms.
- New desktop capability must remain usable offline when its data and dependencies are local.
- Provider-dependent functionality remains capability-gated by accepted provider evidence.

## Rejected alternatives

- Native macOS application: rejected because it duplicates the frontend and conflicts with Linux and Windows goals.
- Qt/PySide as the primary UI: rejected because it does not fit the accepted web-primary application direction as well as a web frontend in a desktop shell.
- Packaged browser-only UI: rejected because it provides a weaker installation, update, credential, notification, lifecycle, and consumer-desktop experience.
- Rewriting the Python core in Rust or TypeScript: rejected because it would discard validated behavior and create duplicate analytical authority.

## Exit and reconsideration

D1 must prove sidecar lifecycle, version negotiation, profile safety, supported-platform packaging, accessibility viability, and Quality integration. If those gates fail materially, a superseding ADR may select Electron while preserving the Python application-service boundary.
