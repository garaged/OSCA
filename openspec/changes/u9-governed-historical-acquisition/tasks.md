# Tasks: U9 Governed Historical Acquisition

## 1. Specification and governance

- [ ] Confirm U9 intent, governing REQ identifiers, ADR constraints, and explicit non-goals.
- [ ] Capture current Kraken capability, quota, history, timestamp, retention, attribution, and failure evidence for the U9 use case.
- [ ] Evaluate no-cost equity candidates against the provider admission gate.
- [ ] Record the equity-provider decision or a blocked decision with exact evidence; do not select implicitly.
- [ ] Finalize versioned acquisition request, outcome, policy-evidence, and structured-status contracts.

## 2. Tests before implementation

- [ ] Add provider capability and policy contract tests.
- [ ] Add golden fixtures for successful, partial, malformed, duplicate, corrected, and gapped responses.
- [ ] Add unsupported asset/interval/range and ambiguous-mapping tests.
- [ ] Add quota, rate-limit, timeout, outage, retry, and cancellation tests.
- [ ] Add secret canary and portable-evidence exclusion tests.
- [ ] Add idempotent repeated/concurrent retrieval tests.
- [ ] Add canonical revision and parser/provider-correction tests.
- [ ] Add CLI help, structured output, exit-code, and remediation tests.
- [ ] Add architecture tests for dependency direction and persistence ownership.

## 3. Provider-neutral application implementation

- [ ] Implement canonical historical acquisition request validation.
- [ ] Implement instrument and verified mapping resolution.
- [ ] Implement capability, policy, and provider-routing resolution.
- [ ] Implement idempotent durable retrieval-job lifecycle.
- [ ] Implement bounded network retrieval orchestration with timeout, retry, rate-limit, cancellation, and response-size controls.
- [ ] Implement raw-payload retention or explicit non-retention evidence according to policy.
- [ ] Implement parser, normalization, deterministic quality validation, and quarantine/rejection behavior.
- [ ] Implement immutable dataset revision creation and complete lineage metadata.
- [ ] Implement structured outcome, audit, telemetry, and operator remediation.

## 4. Provider adapters

- [ ] Reconcile Kraken adapter behavior with U9 historical acquisition contracts.
- [ ] Add Kraken historical fixtures and end-to-end canonical-storage coverage.
- [ ] Implement the admitted equity adapter only after governance approval.
- [ ] Add equity fixtures and conformance coverage when admitted.
- [ ] Ensure provider adapters never write canonical storage directly.

## 5. Operator surfaces

- [ ] Add the primary `osca historical-data fetch` command or an approved equivalent.
- [ ] Preserve local CSV import as the documented offline fallback.
- [ ] Expose provider, capability, policy, revision, quality, and outcome summaries without leaking secrets.
- [ ] Add optional machine-readable output consistent with existing CLI conventions.
- [ ] Provide actionable remediation for blocked and failed outcomes.

## 6. Integration

- [ ] Prove the acquired revision is accepted by the U8 research pipeline.
- [ ] Prove the analyst workspace discovers the resulting dataset and evidence.
- [ ] Prove provider disablement does not remove or corrupt accepted revisions.
- [ ] Prove CSV fallback and network acquisition produce compatible canonical contracts.

## 7. Validation

- [ ] Run Ruff.
- [ ] Run strict mypy.
- [ ] Run the complete pytest suite.
- [ ] Run OpenSpec doctor and strict validation.
- [ ] Run secret scanning, document-link checks, migration checks, and architecture checks.
- [ ] Complete clean-profile manual acceptance for Kraken.
- [ ] Complete clean-profile manual acceptance for the admitted equity path, or retain the blocked provider decision evidence.
- [ ] Exercise outage/quota and malformed-response manual scenarios.

## 8. Documentation and traceability

- [ ] Update README current-state and start-here navigation.
- [ ] Update `docs/testing/manual-testing.md` with U9 commands and acceptance evidence.
- [ ] Document provider attribution, terms, quota, retention, adjustment, and limitation behavior.
- [ ] Document CSV fallback and troubleshooting.
- [ ] Update requirement/spec/test/implementation traceability.
- [ ] Retain milestone evidence and residual limitations.

## Completion rule

No task is complete merely because code exists. U9 closes only when specification, tests, implementation, hosted validation, documentation, traceability, manual acceptance, provider-policy evidence, and residual risks are all retained and reviewable.
