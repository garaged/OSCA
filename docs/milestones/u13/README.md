# U13 — Release-Candidate Acceptance

- **Status:** In progress
- **Baseline:** U12 merged through PR #75 at `8902b256375e3b6fdeb8ba613435cb974ab36562`
- **Branch:** `agent/u13-release-candidate-acceptance`

## Intent

Define, execute, and retain the official threshold for OSCA's first usable release candidate without weakening existing provider, evidence, extension, or execution safety boundaries.

## Exit outcome

The official acceptance matrix passes on supported clean environments, no critical or high-severity defects remain, release artifacts and evidence are traceable, and an explicitly approved release-candidate version and tag are created.

## Acceptance matrix

1. Installation and initialization
2. No-cost historical acquisition
3. Local CSV fallback
4. Dataset quality, revision, and lineage
5. Deterministic analysis
6. Backtesting and paper evidence
7. ML experiment and diagnostics
8. Human-gated validation
9. Workspace browsing and evidence export
10. Backup and restore
11. Extension boundaries
12. Offline operation
13. Provider outage, quota, and policy behavior
14. Corrupt and incomplete artifact handling
15. Upgrade and rollback
16. Documentation and CLI agreement

## Defect threshold

- Critical: zero open defects.
- High: zero open defects.
- Medium: permitted only with explicit documented disposition, workaround, owner, and target milestone.
- Low: permitted when documented and non-blocking.

## Release authority

U13 owns release-candidate version selection, release notes, artifact verification, acceptance evidence, and tag recommendation. Publication/signing remain explicit decisions and are not implied by tagging.

## Safety boundaries

Recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled. ADR-0044 remains NO-GO and P17 remains blocked.
