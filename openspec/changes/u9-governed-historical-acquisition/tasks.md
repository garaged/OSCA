# Tasks: U9 Governed Historical Acquisition

## 1. Specification and governance

- [x] Confirm U9 intent, governing REQ identifiers, ADR constraints, and explicit non-goals.
- [x] Capture current Kraken capability, quota, history, timestamp, retention, attribution, and failure evidence for the U9 use case.
- [x] Evaluate no-cost equity candidates against the provider admission gate.
- [x] Record the blocked equity-provider decision with exact evidence; no source was selected implicitly.
- [x] Finalize versioned acquisition request, outcome, job, policy-evidence, and structured-status contracts.

## 2. Tests before implementation

- [x] Add provider capability and policy contract tests.
- [x] Add deterministic fixtures for successful, partial, malformed, corrupt, corrected, and bounded responses.
- [x] Add unsupported range and ambiguous-mapping tests.
- [x] Add quota, outage, retry, cancellation, and recovery tests.
- [x] Retain inherited P13 endpoint/secret boundaries; Kraken uses no credentials and portable evidence contains no secret values.
- [x] Add idempotent repeated/concurrent retrieval tests.
- [x] Add canonical revision and parser/normalizer-correction tests.
- [x] Add CLI discovery, structured output, exit-code, and remediation tests.
- [x] Preserve architecture checks for dependency direction and canonical persistence ownership.

## 3. Provider-neutral application implementation

- [x] Implement canonical historical acquisition request validation.
- [x] Implement venue context and verified provider mapping resolution.
- [x] Implement capability, policy, and provider-routing resolution.
- [x] Implement idempotent persisted retrieval-job lifecycle.
- [x] Implement bounded network retrieval orchestration using inherited timeout, retry, endpoint, response-size, and explicit opt-in controls plus U9 cancellation/recovery.
- [x] Implement policy-permitted raw-payload retention and digest evidence.
- [x] Implement parser, normalization, deterministic quality validation, and invalid/corrupt rejection behavior.
- [x] Implement immutable processing-aware dataset revisions and complete lineage metadata.
- [x] Implement structured outcomes, audit identities, attempt/timing telemetry, and operator remediation.

## 4. Provider adapters

- [x] Reconcile Kraken adapter behavior with U9 historical acquisition contracts.
- [x] Add Kraken historical fixtures and end-to-end canonical-storage coverage.
- [x] Do not implement an equity adapter because no candidate passed governance approval.
- [x] Retain blocked-equity conformance coverage and governed CSV fallback instead of an unapproved adapter.
- [x] Ensure provider adapters never write canonical storage directly.

## 5. Operator surfaces

- [x] Add primary `osca historical-data fetch` with timezone-safe ISO-8601 parsing.
- [x] Preserve local CSV import as the documented offline fallback.
- [x] Expose provider, mapping, policy, revision, quality, lifecycle, and outcome summaries without leaking secrets.
- [x] Emit machine-readable JSON consistent with existing CLI conventions.
- [x] Provide actionable remediation for blocked, degraded, cancelled, and failed outcomes.

## 6. Integration

- [x] Prove the acquired revision is accepted by the U8 research pipeline.
- [x] Prove the analyst workspace discovers the complete existing dataset and evidence chain.
- [x] Preserve accepted revisions independently of provider availability; reuse validates required canonical artifacts before returning evidence.
- [x] Prove CSV fallback and network acquisition produce compatible canonical contracts.

## 7. Validation

- [x] Run Ruff.
- [x] Run strict mypy.
- [ ] Run the final complete pytest/contracts/migrations/links/architecture suite after the last documentation commit.
- [x] Run OpenSpec doctor and strict validation.
- [x] Run secret scanning, document-link checks, migration checks, and architecture checks.
- [x] Complete clean-profile manual acceptance for Kraken under the predecessor evidence schema.
- [x] Retain the blocked equity-provider decision evidence instead of admitting an unsupported path.
- [x] Exercise outage, quota, corrupt, invalid, partial, stale, cancellation, and recovery scenarios deterministically in hosted tests; public failures are not induced manually.
- [ ] Retain a final clean-profile workspace `--snapshot` after the v2 contract upgrade.

## 8. Documentation and traceability

- [ ] Update README current-state and next-milestone navigation after final Quality.
- [x] Update `docs/testing/manual-testing.md` with U9 commands and acceptance evidence.
- [x] Document provider attribution, terms, quota, retention, correction, and limitation behavior.
- [x] Document CSV fallback and degraded-outcome troubleshooting.
- [x] Update requirement/spec/test/implementation traceability.
- [x] Retain milestone evidence and residual limitations.

## Completion rule

U9 closes only after the final hosted Quality run is green and the clean-profile workspace snapshot is retained. Dedicated workspace sections and detail views remain U10; complete recursive evidence discovery is explicitly part of U9 and is covered by automated regression.
