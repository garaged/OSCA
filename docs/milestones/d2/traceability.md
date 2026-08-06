# D2 Traceability — Desktop Shell and User Experience Foundation

- **Status:** In progress
- **Governing intent:** `docs/milestones/d2/intent.md`
- **Executable specification:** `docs/milestones/d2/specification.md`
- **Requirements:** `docs/governance/requirements-catalog-d2.md`
- **OpenSpec change:** `openspec/changes/d2-desktop-shell-ux-foundation/`
- **Draft pull request:** #81

## Requirement mapping

| Requirement | D2 behavior | Implementation | Automated evidence | Manual evidence/status |
|---|---|---|---|---|
| REQ-0282 | Responsive shell and honest navigation | `apps/desktop/src/App.tsx`, `apps/desktop/src/styles.css` | `apps/desktop/tests/app-shell.test.mjs`; TypeScript/Vite build | Narrow and desktop viewport checks pending |
| REQ-0283 | First-run and persistent disclosures | `desktop.bootstrap`; onboarding and permanent footer | `tests/test_d2_desktop_api.py`; shell render test | Disclosure order/content check pending |
| REQ-0284 | Python-authoritative profile flows | `src/osca/desktop_api/service.py` delegates to operator/lifecycle services | D1/D2 desktop API tests; architecture source test | Clean-profile create/select/open pending |
| REQ-0285 | Safe targets and profile lock | `profile_lock.py`; profile validation and rollback | Non-empty, missing, relative-path, and lock-contention tests | Locked/unwritable-path checks pending |
| REQ-0286 | Loading/empty/error/retry states | React async/action state, `StatePanel`, `ActionFeedback`, `AppErrorBoundary` | Build and initial loading/error architecture tests | Retry and error-focus checks pending |
| REQ-0287 | System diagnostics | `system.diagnostics`; System surface | Desktop API tests; TypeScript response validation/build | Profile/no-profile diagnostics pending |
| REQ-0288 | Synthetic offline sample | Bundled CSV plus canonical `import_local_ohlcv` delegation | Idempotency, lineage, offline and boundary tests | Two-import identity check pending |
| REQ-0289 | Keyboard/focus accessibility | skip link, semantic landmarks, heading/error refs, native controls | Shell render assertions | Keyboard-only and screen-reader checks pending |
| REQ-0290 | Tokens, contrast, motion | semantic CSS variables, light/dark, reduced-motion and forced-colors rules | CSS/build inspection | Contrast, reduced-motion, light/dark checks pending |
| REQ-0291 | Narrow API boundary | typed `desktop_request`; no generic Tauri capability | frontend source architecture test; Rust fmt/clippy | Dependency/capability inspection pending |
| REQ-0292 | No recommendation/live execution | contracts, diagnostics, navigation and permanent UI disclosures | Python negative/boundary tests; shell assertions | Universal deferred-boundary check pending |
| REQ-0293 | Evidence-based completion | specification, catalog, OpenSpec, tests, docs, hosted validation | Quality and Desktop Foundation workflows | Supported-platform manual acceptance and exit review pending |

## Product traceability rows

D2 realizes the following accepted desktop product traceability outcomes:

- usable desktop onboarding and system diagnostics;
- preserved free/offline foundational functionality;
- accessibility, localization-ready design-system, reliability, and performance foundations;
- one authoritative local-first core across adapters;
- permanent no-live-order proof.

## Current implementation disposition

### Implemented

- Versioned D2 desktop application methods and strict response handling.
- Responsive Home/System shell and unavailable-state treatment for deferred navigation.
- Profile list, inspection, creation, selection, opening, bounded locks, and persisted desktop preference state.
- Structured diagnostics and deterministic offline synthetic sample import.
- Reusable semantic design tokens, application state primitives, focus foundations, and error boundary.
- Automated Python, TypeScript build, React shell, frontend architecture, Rust formatting, and Clippy gates.

### Deferred by accepted scope

- Native profile-directory chooser; the current D2 surface accepts an explicit absolute path while preserving the no-frontend-filesystem boundary.
- Provider and credential setup, acquisition, and provider-specific onboarding: D3.
- Research/evidence production surfaces: later dependent milestones.
- Production accessibility completion, localization, and full visual-regression matrix: D18, without weakening D2 foundational gates.

### Prohibited

- Recommendations in D2.
- Broker/exchange connectivity or live-order submission.
- Autonomous or real-capital execution.
- Generic frontend/Rust filesystem or shell access.
- Synthetic data represented as real provider history.

## Exit blockers

- Complete the D2 manual acceptance procedure on macOS ARM64 and Linux x86-64.
- Retain final hosted full supported-platform validation, including the deferred D1 obligation.
- Resolve defects from manual/accessibility validation.
- Complete D2 exit review and owner acceptance.
