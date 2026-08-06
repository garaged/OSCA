# D2 Desktop Shell and User Experience Foundation

- **Status:** In progress
- **Intent:** `intent.md`
- **Executable specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d2.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **OpenSpec:** `../../../openspec/changes/d2-desktop-shell-ux-foundation/`
- **Draft PR:** #81

## Outcome

D2 turns the D1 developer preview into the first honest desktop product surface: a responsive application shell, safe offline onboarding, Python-authoritative profile flows, bounded diagnostics, deterministic synthetic sample import, reusable UI foundations, and explicit accessibility and failure-state behavior.

## Current implementation

- Responsive Home and System surfaces.
- Research and Evidence destinations are visible but explicitly unavailable until later milestones.
- First-run safety disclosures and permanent product-boundary footer.
- Versioned desktop state with known/selected profile references.
- Profile inspect, create, select, open, compatibility, writability, and bounded lock handling.
- System diagnostics and application-level error handling.
- Deterministic offline synthetic sample import through the canonical Python import service.
- Semantic design tokens, light/dark scheme support, reduced-motion and forced-colors foundations.
- Python API tests, frontend render/architecture tests, TypeScript build, Rust format/Clippy, Quality, OpenSpec, and secret-scan integration.

## Deliberate limitations

- The profile path is entered explicitly. A native directory picker is not yet exposed because D2 does not authorize broad frontend filesystem access; a later narrow Rust dialog capability may replace the text-only selection without changing Python authority.
- Provider and credential setup remain D3 scope.
- Research and evidence production workspaces remain later milestone scope.
- D2 establishes accessibility foundations; full release-wide accessibility/localization completion remains D18.

## Exit state

D2 is not ready to merge or exit yet. Remaining gates:

1. finish supported-platform hosted validation including the deferred D1 obligation;
2. execute and retain macOS ARM64 and Linux x86-64 manual acceptance;
3. correct all defects found by accessibility and clean-profile testing;
4. complete exit review;
5. receive explicit owner direction before merge.
