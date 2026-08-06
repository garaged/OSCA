# D2 Desktop Shell and User Experience Foundation

- **Status:** In progress; automated draft validation green
- **Intent:** `intent.md`
- **Executable specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d2.md`
- **Traceability:** `traceability.md`
- **Validation evidence:** `validation-evidence.md`
- **Manual acceptance:** `manual-acceptance.md`
- **OpenSpec:** `../../../openspec/changes/d2-desktop-shell-ux-foundation/`
- **Draft PR:** #81

## Outcome

D2 turns the D1 developer preview into the first honest desktop product surface: a responsive application shell, safe offline onboarding, Python-authoritative profile flows, bounded diagnostics, deterministic synthetic sample import, reusable UI foundations, and explicit accessibility and failure-state behavior.

## Current implementation

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
- Python API/launcher tests, frontend render/architecture tests, TypeScript build, Rust format/unit/Clippy gates, Quality, OpenSpec, secret scanning, wheel-content verification, and Linux package smoke evidence.

## Deliberate limitations

- The profile path is entered explicitly. A native directory picker was evaluated and deferred because D2 does not authorize broad frontend filesystem access; a later narrow Rust dialog capability may replace the text-only selection without changing Python authority.
- Provider and credential setup remain D3 scope.
- Research and evidence production workspaces remain later milestone scope.
- D2 establishes accessibility foundations; full release-wide accessibility/localization completion remains D18.

## Automated validation state

On source commit `04ca5fa130b88b067459af6908a19239f20065c9`:

- Quality run `31066345447` passed.
- Desktop Foundation run `31066345445` passed its draft Python, frontend, Rust-format, Rust-unit-test, and Clippy jobs.
- The D1 deferred Linux package obligation was fulfilled and repeated in retained package-smoke runs documented in `validation-evidence.md`.
- Private vulnerability reporting is enabled, owner-configured secret protections are recorded, and hosted full-history secret scanning passes.

## Exit state

D2 is not ready to merge or exit yet. Remaining gates:

1. run the final non-draft Linux package smoke and Linux/macOS contributor/package-lifecycle matrix on the accepted head;
2. execute and retain macOS ARM64 and Linux x86-64 D2 manual acceptance, including keyboard, screen-reader, responsive, profile, diagnostics, and synthetic-sample checks;
3. correct any defects found by manual/accessibility testing;
4. complete D2 exit review;
5. receive explicit owner direction before changing PR #81 from draft or merging it.
