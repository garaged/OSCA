# D2 Validation Evidence

- **Status:** Complete; automated and supported-platform manual evidence accepted
- **Pull request:** #81
- **Accepted implementation commit:** `806cd74321a8479dddc0d43f8d04c9ca159a9040`
- **Acceptance date:** 2026-08-05 (America/Mexico_City)
- **Baseline relationship:** the accepted D2 head was verified as zero commits behind `main` before exit closeout.

## Final ready-state automated evidence

### Quality

- Workflow: `Quality`
- Run: `31067445581`
- Source: `806cd74321a8479dddc0d43f8d04c9ca159a9040`
- Conclusion: success

Passing jobs included:

- full Ruff validation;
- strict mypy;
- complete Python tests, contracts, migrations, links, and architecture checks;
- trusted-local extension conformance;
- OpenSpec doctor and strict validation;
- full-history hosted secret scanning;
- contributor rehearsal on Linux x86-64;
- contributor rehearsal on macOS ARM64;
- package lifecycle on Linux x86-64;
- package lifecycle on macOS ARM64.

### Desktop Foundation

- Workflow: `Desktop Foundation`
- Run: `31067445632`
- Source: `806cd74321a8479dddc0d43f8d04c9ca159a9040`
- Conclusion: success

Passing jobs included:

- focused desktop Ruff;
- strict desktop mypy;
- D1/D2 desktop API and launcher tests;
- bundled synthetic sample presence in the built Python wheel;
- TypeScript production build;
- React shell and frontend architecture tests;
- Rust formatting;
- Rust unit tests;
- Clippy with warnings denied;
- final Debian desktop package build;
- bounded Xvfb packaged-binary launch smoke;
- Debian package inspection and artifact upload.

Final package artifact:

- Name: `osca-d1-d2-linux-desktop-package`
- Artifact ID: `8954390248`
- Size: 2,866,079 bytes
- Digest: `sha256:82f8447a05e988a1e820ed074e1aec8f1299643607f71d27f00c2ed7f435e44a`
- Expiry: 2026-11-04

## Earlier retained Linux package evidence

The deferred D1 Linux hosted-validation obligation was fulfilled and then repeated during D2:

- Run `31065065075`, source `112726750c6a1bd060ddc29dc840af83dbd68480`, artifact `8953603913`, digest `sha256:30f625f0fce137b4b01cd0903c9ae5c06a285bef6019310340f05da72053501a`.
- Run `31065891295`, source `3e5837fe30a56573bf45cc1fdcee4ac3c7f97f98`, artifact `8953859616`, digest `sha256:c7f4e5377e522fb1cdcea93aad11ecef7f0f0a6d801ff8179fcdddd8bbb1d43f`.

The final ready-state run supersedes these as the accepted D2 package evidence while the earlier artifacts remain useful historical proof that the D1 exception was closed.

## Supported-platform manual acceptance

The repository owner reported that the complete D2 manual-acceptance procedure passed on both supported platforms:

### macOS ARM64

- Result: pass.
- Clean first-run disclosures and deferred navigation: pass.
- Keyboard-only navigation, focus placement, and error-summary behavior: pass.
- VoiceOver landmarks, labels, headings, status, and error announcements: pass.
- Narrow, intermediate, and normal desktop layouts: pass.
- Missing and non-empty profile safety: pass.
- Profile create/select/open persistence: pass.
- Lock-contention behavior: pass.
- Synthetic sample imported twice with stable governed identity: pass.
- Diagnostics and sidecar-failure behavior: pass.
- Reduced motion, light/dark, contrast, and permanent boundaries: pass.
- Network observation: no unexplained external activity reported.
- Defects: none reported.

### Linux x86-64

- Result: pass.
- Clean first-run disclosures and deferred navigation: pass.
- Keyboard-only navigation, focus placement, and error-summary behavior: pass.
- Orca landmarks, labels, headings, status, and error announcements: pass.
- Narrow, intermediate, and normal desktop layouts: pass.
- Missing and non-empty profile safety: pass.
- Profile create/select/open persistence: pass.
- Lock-contention behavior: pass.
- Synthetic sample imported twice with stable governed identity: pass.
- Diagnostics and sidecar-failure behavior: pass.
- Reduced motion, appearance/contrast, and permanent boundaries: pass.
- Network observation: no unexplained external activity reported.
- Defects: none reported.

Detailed machine-local screenshots, logs, environment reports, and path-bearing evidence were intentionally retained outside the repository to avoid publishing private paths or host-specific material. This document records the owner-accepted disposition without claiming that the connected integration inspected those private artifacts.

## Security evidence

- GitHub reports private vulnerability reporting as enabled.
- The repository owner confirmed enabling secret-protection settings.
- The connected integration cannot enumerate every native secret-scanning subfeature, so no unsupported claim is made about individual options.
- Independent hosted full-history `gitleaks` scanning passes on the accepted D2 head.
- The production Tauri CSP is local-only; the development CSP permits only the local Vite origin and Tauri IPC.
- No provider, credential, recommendation, broker, exchange, autonomous, live-order, or real-capital capability is enabled.

## Final disposition

All D2 automated, supported-platform manual, accessibility-foundation, safety-boundary, package, evidence, and traceability gates passed. No release-blocking defect was reported. D2 is accepted for merge subject only to explicit repository-owner merge direction.
