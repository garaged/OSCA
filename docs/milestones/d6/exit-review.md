# D6 Exit Review — Research Projects, Saved Workspaces, and Integrated Evidence

- **Status:** Accepted
- **Pull request:** [#86](https://github.com/garaged/OSCA/pull/86)
- **Baseline:** D5 merge `1936f1e5b47055f1e8d88d293abaf9dc99c00970`
- **Validated candidate:** `71ae3e7249cc09b735b82fa7b2a215a142bcabd3`

## Delivered outcome

D6 adds a profile-scoped research project surface for organizing governed evidence without introducing recommendations, executable notebooks, provider credential collection, brokerage connectivity, paper orders, or real-capital execution.

Delivered implementation includes:

- profile-scoped project persistence with versioned SQLite storage;
- project create/list/get/update/archive/restore/delete and clone lifecycle;
- typed evidence pins for governed resources, including degraded-state disclosure;
- bounded user-authored notes kept separate from authoritative analytical output;
- saved project workspace definitions that store declarative context only;
- append-only timeline records for project events;
- governed thin manifest export with schema/version, provenance, digest, user-note labeling, and non-self-contained disclosure;
- narrow desktop `project.*` application methods through the existing `desktop_request` bridge;
- Projects desktop UI and shell navigation with source-boundary, responsive, and accessibility regression coverage.

## Requirements and architecture disposition

Requirements `REQ-0341` through `REQ-0356` are allocated across the D6 specification, OpenSpec capability, planned implementation, tests, manual-acceptance procedure, traceability, validation evidence, and this review.

The automated implementation evidence supports the required project lifecycle, pins, notes, timeline, workspace, manifest export, ownership, profile isolation, source-boundary, and responsive/accessibility behaviors. Python remains authoritative for project state and validation; Rust remains the transport/session broker; React renders typed state and declarative intent.

One naming observation remains from final review: D6 uses `src/osca/desktop_api/d6_service.py`, matching the current desktop milestone convention. The externally meaningful contract is still the stable `project.*` method family, so this is not a D6 blocker. Before desktop APIs are treated as a stable public extension surface, milestone-named implementation modules should be renamed or consolidated into capability-named services.

Disposition: accepted.

## Automated validation disposition

Local validation passed:

- Ruff on touched D6 Python and test files;
- strict mypy on new D6 backend files/tests;
- D6 project-service tests: 5 passed;
- focused D5+D6 backend suite: 15 passed;
- focused D1-D6 desktop Python suite: 52 passed;
- D6-focused desktop frontend tests: 26 passed;
- full desktop frontend source tests: 26 passed;
- desktop TypeScript check;
- desktop Vite production build;
- OpenSpec strict validation: 50 passed, 0 failed.

Hosted validation passed on exact head `71ae3e7249cc09b735b82fa7b2a215a142bcabd3`:

- Quality run `31742179590`: success;
- Desktop Foundation run `31742179591`: success.

Local Rust format/tests/Clippy were not run because `cargo` is unavailable in this sandbox. Hosted Desktop Foundation passed the Rust broker checks on the exact candidate.

Disposition: pass.

## Supported-platform manual acceptance

- macOS ARM64: PASS, owner-reported clean-profile manual acceptance.
- Linux x86-64: PASS, owner-reported clean-profile manual acceptance.

The owner reported all D6 manual checks passed. The section 8 ownership case intentionally failed closed when the same active profile/project was opened in a second window, which is accepted for D6 because it prevents concurrent mutable ownership rather than sharing project state across owners.

Disposition: pass.

## Exit decision

**D6 exit decision: ACCEPTED.**
