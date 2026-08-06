# Tasks: D2 Desktop Shell and User Experience Foundation

## Specification and governance

- [x] Convert D2 intent into an executable milestone specification.
- [x] Allocate REQ-0282 through REQ-0293.
- [x] Add D2 OpenSpec proposal and delta specification.
- [x] Add D2 traceability and implementation disposition.
- [x] Add clean-profile manual acceptance procedure.
- [x] Retain automated draft validation evidence.
- [ ] Retain final non-draft supported-platform validation and exit review.

## Python application service

- [x] Add versioned desktop state and known-profile references.
- [x] Serialize desktop state updates across short-lived sidecar processes.
- [x] Add profile list, inspect, create, select, and open methods.
- [x] Delegate profile creation and diagnostics to canonical Python services.
- [x] Add bounded inter-process profile mutation locks.
- [x] Reject unsafe, relative, non-empty, unavailable, and locked profiles.
- [x] Make profile creation failure-atomic and defer open-state persistence until final validation.
- [x] Add typed system diagnostics.
- [x] Add deterministic bundled synthetic sample import through canonical local import.
- [x] Preserve the D1 health and legacy inspection contract.

## React and Rust desktop shell

- [x] Add strict typed response validation.
- [x] Add responsive Home and System surfaces.
- [x] Align the native minimum window width with the 320 CSS-pixel responsive requirement.
- [x] Mark Research and Evidence as unavailable rather than functional placeholders.
- [x] Add onboarding and permanent safety disclosures.
- [x] Add loading, empty, unavailable, retry, action-error, and app-error surfaces.
- [x] Add keyboard/focus, skip-link, reduced-motion, light/dark, and forced-colors foundations.
- [x] Add restrictive production and localhost-only development CSPs.
- [x] Preserve one narrow `desktop_request` Rust command.
- [x] Bound IPC requests/responses, timeout sidecar calls, require one response, and redact raw stderr.
- [x] Add a canonical launcher that uses the locked `uv` Python interpreter.
- [x] Evaluate and defer a narrow native directory-dialog capability without granting frontend filesystem access.

## Validation and evidence

- [x] Add focused Python D2 contract, safety, lock, rollback, state, sample, and launcher tests.
- [x] Add frontend shell render and architecture tests without new dependencies.
- [x] Add strict TypeScript build, Rust format, Rust unit, and Clippy gates.
- [x] Verify the bundled synthetic CSV is retained in the Python wheel.
- [x] Run draft hosted Quality successfully on the accepted implementation head.
- [x] Complete the reconciled draft Desktop Foundation run.
- [x] Fulfill the deferred D1 Linux x86-64 desktop package and launch-smoke obligation.
- [ ] Run the final ready-for-review Linux package smoke.
- [ ] Run the full supported Linux/macOS contributor and package-lifecycle matrix.
- [ ] Execute macOS ARM64 manual acceptance.
- [ ] Execute Linux x86-64 manual acceptance.
- [ ] Resolve manual/accessibility defects.
- [ ] Complete D2 exit review.
