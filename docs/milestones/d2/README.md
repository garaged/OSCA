# D2 Desktop Shell and User Experience Foundation

- **Status:** Complete; exit review passed and ready for owner-directed merge
- **Intent:** `intent.md`
- **Executable specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d2.md`
- **Traceability:** `traceability.md`
- **Validation evidence:** `validation-evidence.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d2-desktop-shell-ux-foundation/`
- **Pull request:** #81

## Outcome

D2 turns the D1 developer preview into the first honest desktop product surface: a responsive application shell, safe offline onboarding, Python-authoritative profile flows, bounded diagnostics, deterministic synthetic sample import, reusable UI foundations, and explicit accessibility and failure-state behavior.

## Delivered implementation

- Responsive Home and System surfaces.
- Research and Evidence destinations are visible but explicitly unavailable until later milestones.
- First-run safety disclosures and permanent product-boundary footer.
- Versioned desktop state with known/selected profile references and serialized inter-process writes.
- Profile inspect, create, select, open, compatibility, writability, failure-atomic creation, and bounded lock handling.
- System diagnostics and application-level error handling.
- Deterministic offline synthetic sample import through the canonical Python import service.
- Semantic design tokens, light/dark scheme support, reduced-motion and forced-colors foundations.
- Restrictive production CSP and localhost-only development CSP.
- Bounded Rust broker with one-request/one-response validation, 1 MiB limits, 15-second timeout, and ordinary-user stderr redaction.
- Canonical development launcher that pins the sidecar to the locked `uv` Python interpreter.
- Python API/launcher tests, frontend render/architecture tests, TypeScript build, Rust format/unit/Clippy gates, Quality, OpenSpec, secret scanning, wheel-content verification, supported-platform lifecycle validation, and Linux package smoke evidence.

## Deliberate limitations

- The profile path is entered explicitly. A native directory picker was evaluated and deferred because D2 does not authorize broad frontend filesystem access; a later narrow Rust dialog capability may replace the text-only selection without changing Python authority.
- Provider and credential setup remain D3 scope.
- Research and evidence production workspaces remain later milestone scope.
- D2 establishes accessibility foundations; full release-wide accessibility/localization completion remains D18.

## Final automated validation

On accepted implementation commit `806cd74321a8479dddc0d43f8d04c9ca159a9040`:

- Quality run `31067445581` passed.
- Linux x86-64 and macOS ARM64 contributor rehearsals passed.
- Linux x86-64 and macOS ARM64 package-lifecycle jobs passed.
- Desktop Foundation run `31067445632` passed its Python, frontend, Rust, and final Linux desktop package-smoke jobs.
- Final Linux package artifact `8954390248` has digest `sha256:82f8447a05e988a1e820ed074e1aec8f1299643607f71d27f00c2ed7f435e44a`.
- Private vulnerability reporting is enabled, owner-configured secret protections are recorded, and hosted full-history secret scanning passes.

## Manual acceptance

The repository owner reported successful D2 manual acceptance on both supported platforms on 2026-08-05:

- macOS ARM64;
- Linux x86-64.

The accepted checks covered clean-profile behavior, profile safety and persistence, keyboard and screen-reader operation, narrow and desktop layouts, reduced motion and appearance, diagnostics, sidecar failure handling, lock contention, deterministic two-import synthetic sample behavior, deferred capability boundaries, and absence of unexplained external network activity. No manual or accessibility defects were reported. Machine-local screenshots and logs remain outside the repository to avoid retaining private paths or host-specific material.

## Exit state

All D2 specification, implementation, automated validation, supported-platform manual acceptance, traceability, and exit-review gates are satisfied. PR #81 is ready to merge once the repository owner gives explicit merge direction.
