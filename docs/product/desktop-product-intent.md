# Desktop Product Intent

Status: Accepted product authority

## Purpose

OSCA will evolve from a capable local-first research core and browser evidence workspace into a broadly usable desktop application for market research, quantitative analysis, explainable recommendations, machine-learning experimentation, and simulated portfolio evaluation.

## Product outcomes

The desktop product must let a user discover assets, acquire or import governed data, perform deterministic analysis, build and evaluate strategies, run bounded ML experiments, review evidence-backed recommendations, and evaluate decisions in virtual portfolios without requiring paid services for the foundational workflow.

## Permanent boundaries

- OSCA is research and simulation software, not financial advice.
- Deterministic services remain authoritative for calculations, fills, accounting, risk, eligibility, and recommendation records.
- Generative AI may explain and summarize evidence but may not replace numerical authority.
- No broker or exchange order submission, live-order adapter, real-capital execution, or unattended real trading is permitted.
- Provider capabilities remain unavailable until their licensing, plan, credential, quota, retention, and export evidence passes the accepted promotion gate.
- Extensions remain trusted-local unless OS-enforced containment is proven; manifest validation alone never authorizes execution.
- Telemetry is disabled by default.

## Product architecture intent

The primary desktop stack is Tauri v2 with React and TypeScript for presentation, a small Rust host broker, and the existing Python modular-monolith core as a supervised sidecar. The frontend must call versioned application services and must not duplicate domain calculations or access storage, credentials, providers, or extensions directly.

SQLite remains the authoritative metadata and journal store. Parquet and governed files remain the authoritative bulk-series, feature, model-output, evidence, and report storage.

## Platform and release intent

macOS ARM64 and Linux x86-64 remain first-class. Windows x86-64 must be supported before the first polished release. Development proceeds through `0.2.0-alpha.*`, broader testing through `0.2.0-beta.*`, a complete desktop release candidate as `1.0.0rc1`, and the accepted polished release as `1.0.0`.

## Delivery model

The D1-D19 roadmap is binding at outcome and boundary level. Each milestone receives an intent before implementation and an executable specification when it starts. Later milestone details may evolve from evidence, but changes to product boundaries, release scope, or dependency order require an explicit decision and documentation update.
