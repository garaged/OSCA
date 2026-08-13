# D6 Validation Evidence — Research Projects, Saved Workspaces, and Integrated Evidence

- **Status:** Accepted
- **Pull request:** [#86](https://github.com/garaged/OSCA/pull/86)
- **Branch:** `agent/d6-research-projects-workspaces`
- **Baseline:** D5 merge `1936f1e5b47055f1e8d88d293abaf9dc99c00970`
- **Validated candidate:** `71ae3e7249cc09b735b82fa7b2a215a142bcabd3`

## Automated validation

Local validation passed:

- `uv run ruff check src/osca/desktop_api/projects.py src/osca/desktop_api/d6_service.py src/osca/desktop_api/stdio.py tests/test_d6_desktop_projects.py tests/test_makefile.py`;
- `uv run mypy src/osca/desktop_api/projects.py src/osca/desktop_api/d6_service.py tests/test_d6_desktop_projects.py`;
- `uv run pytest tests/test_d6_desktop_projects.py`: 5 passed;
- `uv run pytest tests/test_d5_desktop_workbench.py tests/test_d6_desktop_projects.py`: 15 passed;
- focused D1-D6 desktop Python suite: 52 passed;
- D6-focused desktop frontend tests: 26 passed;
- full desktop frontend source tests: 26 passed;
- desktop TypeScript check;
- desktop Vite production build;
- `npm run openspec:validate`: 50 passed, 0 failed.

Hosted exact-head validation passed on `71ae3e7249cc09b735b82fa7b2a215a142bcabd3`:

- Quality run `31742179590`: success;
- Desktop Foundation run `31742179591`: success.

The hosted checks include secret scanning, Python/architecture validation, frontend validation, Rust broker validation, and CodeQL checks for the D6 candidate.

Local Rust format/tests/Clippy were not run because `cargo` is unavailable in this sandbox. Hosted Desktop Foundation passed the Rust broker checks on the exact candidate.

## Manual acceptance

The complete procedure in `manual-acceptance.md` must pass from a clean profile on:

- macOS ARM64;
- Linux x86-64.

Private host paths, credentials, provider account information, and machine-local profile identifiers must not be committed.

Supported-platform manual acceptance was completed by the owner on clean profiles after the final D6 UI corrections. The owner reported all D6 manual checks passed, including project lifecycle, workspace save/restore, governed pins, notes/evidence separation, thin manifest export, offline/research-only boundaries, profile isolation/ownership, accessibility/responsiveness, and packaged restart behavior.

For profile isolation and ownership, opening the same active profile/project in a second window failed closed at project/profile open. This is accepted behavior for D6 because it prevents concurrent mutation and preserves profile ownership; the manual disposition is PASS when the user-visible state clearly blocks reuse rather than silently sharing mutable project state.

## Current disposition

- Implementation slices: complete.
- Automated validation: passed on exact head `71ae3e7249cc09b735b82fa7b2a215a142bcabd3`.
- macOS ARM64 manual acceptance: passed.
- Linux x86-64 manual acceptance: passed.
- D6 exit decision: accepted.
