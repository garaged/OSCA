# Tasks: U13 Release-Candidate Acceptance

## Acceptance authority

- [x] Record U13 intent, acceptance matrix, defect threshold, and safety boundaries.
- [x] Define normative acceptance result and defect-disposition schemas.
- [x] Inventory existing U9-U12 evidence and reusable hosted workflows.

## Acceptance implementation

- [x] Add a canonical acceptance runner and machine-readable report.
- [x] Cover all 16 acceptance areas with explicit pass/fail/block outcomes.
- [x] Verify package checksums, SBOM, provenance, version, and platform support.
- [x] Verify no-cost principal demonstration and offline fallback.
- [x] Verify provider-policy, corruption, incomplete-artifact, upgrade, and rollback behavior.
- [x] Verify documentation and canonical CLI agreement.
- [x] Enforce zero critical/high open defects before RC eligibility.

## Release-candidate authority

- [x] Select and apply RC package version `0.1.0rc1`.
- [x] Produce release notes and known-limitations authority.
- [ ] Generate final selected-version RC artifacts and retained acceptance evidence.
- [x] Run the official supported-platform acceptance matrix with the CI placeholder candidate.
- [ ] Reconcile README, manual testing, traceability, and exit review after final selected-version validation.
- [ ] Recommend tag `v0.1.0rc1` only after all blocking gates pass.
