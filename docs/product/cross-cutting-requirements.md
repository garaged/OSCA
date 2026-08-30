# Desktop Cross-Cutting Requirements

Status: Accepted and inherited by D1-D19

## Authority and correctness

- Python application services remain authoritative for market calculations, strategies, backtests, simulation fills, accounting, risk, model eligibility, and recommendation records.
- Frontend and Rust-host code may format, orchestrate, and present authoritative results but must not recreate domain formulas.
- Every material result must retain source, revision, method, configuration, time, and limitation lineage.
- Missing, stale, ambiguous, unauthorized, or failed-quality evidence must produce an explicit unavailable or degraded state rather than fabricated output.

## Security and privacy

- Store secrets in platform credential storage; persist only references and redacted metadata.
- Use least-privilege Tauri capabilities, strict content-security policy, no remote executable content, no shell exposure, and no unrestricted filesystem access.
- Validate all IPC messages, cap payload sizes, reject unknown methods and versions, and avoid local network listeners for the primary desktop boundary.
- Treat imported text, provider text, extension output, and retrieved content as untrusted.
- Keep telemetry disabled by default and expose retention, deletion, cache, network, credential, and support-bundle controls.

## Financial-safety boundaries

- No live-order endpoint, adapter, destination, credential, or real-capital workflow may exist.
- Backtests, forward paper evaluation, virtual-portfolio accounting, recommendations, and user-confirmed simulated actions must remain distinct.
- Recommendation actions may create only an unconfirmed simulated-order draft.
- User-facing surfaces must identify simulation, uncertainty, assumptions, and the non-advisory nature of the product.

## Data and migration

- SQLite stores metadata, configuration, registries, schedules, audit records, and double-entry journals.
- Parquet or governed files store bulk series, features, datasets, model outputs, evidence, and reports.
- Storage changes require preflight, verified backup, forward migration, interruption recovery, idempotence tests, and an explicit rollback or restore declaration.
- Point-in-time datasets must prevent look-ahead leakage and record corporate-action, missing-data, survivorship, timezone, and revision policy.

## Accessibility and localization

- All workflows must be keyboard operable with visible focus and logical focus order.
- Support screen readers, scalable text, high contrast, reduced motion, non-color-only meaning, accessible chart alternatives, and actionable error focus.
- Use stable localization identifiers and locale-aware number, currency, date, market-calendar, and timezone formatting.
- New UI milestones require accessibility and pseudo-localization tests from their first implementation slice.

## Reliability and performance

- Long-running work must be cancellable, observable, restart-aware, and bounded by declared resource policies.
- Sidecar crashes and protocol mismatches must fail visibly and support safe restart without data corruption.
- Large datasets must use paging, range selection, column selection, declared downsampling, and full-resolution export.
- Performance budgets must be defined when a workflow becomes user-facing and must become release-blocking by D18.

## Documentation and verification

Every milestone updates applicable user guidance, methodology, provider documentation, troubleshooting, architecture status, OpenSpec, traceability, manual acceptance, migrations, and known limitations. Automated checks must cover Python, TypeScript, Rust, IPC, architecture, security, accessibility, and relevant domain invariants.

Every new or materially changed top-level desktop area must also update `docs/product/desktop-user-guide.md` before milestone closeout. The guide must explain the area in plain language for a user who is not assumed to be finance-specialized, including its purpose, prerequisites, what it is and is not for, important domain terminology, failure/degraded-state interpretation where relevant, and at least one recommended workflow showing how it connects to the rest of OSCA.

Top-level desktop navigation must expose a concise plain-language purpose for each area. Complex research areas must provide in-app progressive disclosure such as a keyboard-accessible `What do I do here?` guide that explains the recommended order of operations and prerequisite dependencies without duplicating domain calculations.

If a user-visible workflow cannot be explained clearly enough to satisfy that guide, treat the difficulty as product-usability evidence. Prefer simplifying the workflow, improving labels or prerequisites, or adding progressive disclosure rather than documenting accidental complexity as permanent behavior.
