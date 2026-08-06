# D2 Traceability — Desktop Shell and User Experience Foundation

- **Status:** Complete; exit review passed
- **Governing intent:** `docs/milestones/d2/intent.md`
- **Executable specification:** `docs/milestones/d2/specification.md`
- **Requirements:** `docs/governance/requirements-catalog-d2.md`
- **Validation evidence:** `docs/milestones/d2/validation-evidence.md`
- **Exit review:** `docs/milestones/d2/exit-review.md`
- **OpenSpec change:** `openspec/changes/d2-desktop-shell-ux-foundation/`
- **Pull request:** #81

## Requirement mapping

| Requirement | D2 behavior | Implementation | Automated evidence | Manual evidence/status |
|---|---|---|---|---|
| REQ-0282 | Responsive shell and honest navigation | `apps/desktop/src/App.tsx`, `apps/desktop/src/styles.css`, Tauri 320-pixel minimum | Frontend shell tests; TypeScript/Vite build; Desktop Foundation `31067445632` | Passed on macOS ARM64 and Linux x86-64 |
| REQ-0283 | First-run and persistent disclosures | `desktop.bootstrap`; onboarding and permanent footer | D2 desktop API tests; shell render tests | Passed on both supported platforms |
| REQ-0284 | Python-authoritative profile flows | `src/osca/desktop_api/service.py` delegates to operator/lifecycle services | D1/D2 API, launcher, architecture, contributor, and package-lifecycle tests | Clean-profile create/select/open and persistence passed on both platforms |
| REQ-0285 | Safe targets and profile lock | `profile_lock.py`; profile validation, rollback, serialized desktop state | Missing, non-empty, relative-path, partial-failure, state-order, and lock-contention tests | Safety and lock behavior passed on both platforms |
| REQ-0286 | Loading/empty/error/retry states | React async/action state, `StatePanel`, `ActionFeedback`, `AppErrorBoundary` | Build, shell, and architecture tests | Retry, sidecar-unavailable, and error-focus checks passed |
| REQ-0287 | System diagnostics | `system.diagnostics`; System surface | Desktop API tests; strict typed response validation/build | Profile/no-profile diagnostics passed on both platforms |
| REQ-0288 | Synthetic offline sample | Bundled CSV plus canonical `import_local_ohlcv` delegation | Idempotency, lineage, offline, boundary, and wheel-content tests | Two-import stable-identity check passed on both platforms |
| REQ-0289 | Keyboard/focus accessibility | Skip link, semantic landmarks, heading/error refs, native controls | Shell render assertions | Keyboard plus VoiceOver/Orca checks passed |
| REQ-0290 | Tokens, contrast, motion | Semantic CSS variables, light/dark, reduced-motion and forced-colors rules | CSS/build inspection; CSP configuration tests | Responsive, reduced-motion, appearance, and contrast checks passed |
| REQ-0291 | Narrow API boundary | Typed `desktop_request`; bounded Rust broker; locked Python launcher | Frontend architecture test; Rust format/unit/Clippy; launcher tests | Capability and failure-surface inspection passed |
| REQ-0292 | No recommendation/live execution | Contracts, diagnostics, navigation and permanent UI disclosures | Python negative/boundary tests; shell assertions; secret scan | Universal deferred-boundary and network checks passed |
| REQ-0293 | Evidence-based completion | Specification, catalog, OpenSpec, tests, docs, hosted validation | Quality `31067445581`; Desktop Foundation `31067445632`; final artifact `8954390248` | Both supported-platform acceptances passed; exit review complete |

## Product traceability rows

D2 realizes the following accepted desktop product outcomes:

- usable desktop onboarding and system diagnostics;
- preserved free/offline foundational functionality;
- accessibility, localization-ready design-system, reliability, and performance foundations;
- one authoritative local-first core across adapters;
- permanent no-live-order proof.

## Final implementation disposition

### Implemented and accepted

- Versioned D2 desktop application methods and strict response handling.
- Responsive Home/System shell and unavailable-state treatment for deferred navigation.
- Profile list, inspection, failure-atomic creation, selection, opening, bounded profile locks, and serialized persisted desktop preference state.
- Structured diagnostics and deterministic offline synthetic sample import.
- Reusable semantic design tokens, application-state primitives, focus foundations, and error boundary.
- Restrictive production/development CSP configuration.
- Bounded Rust request broker with timeout, payload limits, single-response validation, and stderr redaction.
- Locked-`uv` Python development launcher.
- Automated Python, wheel-content, TypeScript build, React shell, frontend architecture, Rust formatting/unit/Clippy, Quality, OpenSpec, secret-scan, contributor, package-lifecycle, and Linux package-smoke gates.
- Supported-platform manual acceptance on macOS ARM64 and Linux x86-64.

### Evaluated and deferred

- Native profile-directory chooser. The current D2 surface accepts an explicit absolute path while preserving the no-frontend-filesystem boundary. A later narrow host dialog capability may improve selection UX without granting generic filesystem authority.

### Deferred by accepted scope

- Provider and credential setup, acquisition, and provider-specific onboarding: D3.
- Research/evidence production surfaces: later dependent milestones.
- Production accessibility completion, localization, and full visual-regression matrix: D18, without weakening the D2 foundation accepted here.

### Prohibited and verified absent

- Recommendations in D2.
- Broker/exchange connectivity or live-order submission.
- Autonomous or real-capital execution.
- Generic frontend/Rust filesystem or shell access.
- Synthetic data represented as real provider history.

## Exit blockers

None. All D2 requirements and exit gates are satisfied. Merge still requires explicit repository-owner direction.
