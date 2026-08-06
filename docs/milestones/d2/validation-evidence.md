# D2 Validation Evidence

- **Status:** Automated draft evidence retained; final non-draft and manual evidence pending
- **Draft pull request:** #81
- **Current validated implementation commit:** `04ca5fa130b88b067459af6908a19239f20065c9`
- **Baseline relationship:** `agent/d2-desktop-shell` was verified as zero commits behind `main` during D2 implementation.

## Current-head automated evidence

### Quality

- Workflow: `Quality`
- Run: `31066345447`
- Source: `04ca5fa130b88b067459af6908a19239f20065c9`
- Conclusion: success

Retained passing gates include:

- full Ruff validation;
- strict mypy;
- complete Python tests, contracts, migrations, links, and architecture checks;
- trusted-local extension conformance;
- OpenSpec doctor and strict validation;
- full-history hosted secret scanning.

### Desktop Foundation

- Workflow: `Desktop Foundation`
- Run: `31066345445`
- Source: `04ca5fa130b88b067459af6908a19239f20065c9`
- Conclusion: success

Retained passing gates include:

- focused desktop Ruff;
- strict desktop mypy;
- D1/D2 desktop API and launcher tests;
- bundled synthetic sample presence in the built Python wheel;
- TypeScript production build;
- React shell and frontend architecture tests;
- Rust formatting;
- Rust unit tests;
- Clippy with warnings denied.

The Linux package job is intentionally a non-draft or manual-dispatch gate after repeated passing package evidence was retained. This reduces repeated draft build cost without weakening the ready-for-review gate.

## Linux x86-64 package and launch evidence

### Initial hosted fulfillment of deferred D1 obligation

- Workflow run: `31065065075`
- Source: `112726750c6a1bd060ddc29dc840af83dbd68480`
- Result: Debian package build, bounded Xvfb launch smoke, package inspection, and artifact upload passed.
- Artifact: `osca-d1-d2-linux-desktop-package`
- Artifact ID: `8953603913`
- Digest: `sha256:30f625f0fce137b4b01cd0903c9ae5c06a285bef6019310340f05da72053501a`

### Repeated D2-hardened package evidence

- Workflow run: `31065891295`
- Source: `3e5837fe30a56573bf45cc1fdcee4ac3c7f97f98`
- Result: Debian package build, packaged-binary launch smoke, package inspection, and artifact upload passed.
- Artifact: `osca-d1-d2-linux-desktop-package`
- Artifact ID: `8953859616`
- Size: 2,866,181 bytes
- Digest: `sha256:c7f4e5377e522fb1cdcea93aad11ecef7f0f0a6d801ff8179fcdddd8bbb1d43f`
- Expiry: 2026-11-04

The only production-code change after this repeated package run moved the Rust test module after production items to satisfy Clippy; the packaged application behavior did not change. A fresh package smoke remains mandatory when PR #81 becomes ready for review.

## Security evidence

- GitHub reports private vulnerability reporting as enabled.
- The repository owner confirmed enabling secret-protection settings.
- The connected integration cannot enumerate the exact GitHub secret-scanning subfeatures, so no unsupported claim is made about individual push-protection or validity-check options.
- Independent hosted full-history `gitleaks` scanning passes on the current D2 head.
- The production Tauri CSP is local-only; the development CSP permits only the local Vite origin and Tauri IPC.
- No provider, credential, recommendation, broker, exchange, autonomous, live-order, or real-capital capability is enabled.

## Evidence still required before D2 exit

- Ready-for-review Linux package smoke on the final accepted head.
- Linux x86-64 and macOS ARM64 contributor-rehearsal and package-lifecycle jobs.
- macOS ARM64 D2 manual acceptance.
- Linux x86-64 D2 manual acceptance.
- Keyboard-only and screen-reader observations on both supported platforms.
- Narrow and desktop viewport evidence.
- Clean-profile create/select/open, lock-contention, diagnostics, and two-import synthetic-sample evidence.
- Resolution of all defects found during manual/accessibility validation.
- D2 exit review and explicit owner acceptance.
