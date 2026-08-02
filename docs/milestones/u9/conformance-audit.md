# U9 Full Conformance Audit

- **Audit date:** 2026-08-02
- **Milestone:** U9 governed no-cost historical data acquisition
- **Implementation PR:** #72
- **Decision:** Automated spec conformance complete; final manual snapshot pending

## Evidence reviewed

The audit reviewed the U9 planning authority from PR #70, the acquisition foundation from PR #71, the complete PR #72 implementation, hosted Quality results, the real Kraken clean-profile acquisition, the blocked Twelve Data equity result, the retained U8 pipeline manifest, the U9 manual-testing guide, and requirement traceability.

## Resolution of previously material gaps

### Canonical bounded request — resolved

The v2 request contract and primary CLI now provide timezone-aware `start_at` and `end_at`, half-open range filtering, venue context, expected provider pair mapping, freshness limits, minimum rows, and complete-range expectations. Unsupported ranges and mapping mismatches fail without an accepted revision.

### Durable job lifecycle — resolved

U9 persists stable request, correlation, job, and acquisition identities plus job stage, progress, attempts, duration, completion, failure, cancellation, reuse, and interrupted-job recovery. Equivalent concurrent in-process requests share work, and completed equivalent requests reuse accepted evidence while required artifacts remain present.

### Complete degraded-outcome taxonomy — resolved

The contract distinguishes succeeded, fresh, stale, partial, invalid, corrupt, refreshing, quota-blocked, credential-blocked, policy-blocked, provider-unavailable, cancelled, and failed outcomes. Non-success states carry findings and operator remediation; quota outcomes include quota and retry metadata.

### Provider correction lineage — resolved

Raw and normalized digests are retained separately. Parser and normalizer identities participate in processing-aware dataset revision identity. Changed processing produces a new revision with predecessor, supersession, and correction rationale fields rather than silently rewriting history.

### Audit, telemetry, and attempts — resolved

Acquisition evidence retains request/correlation/job/acquisition identities, provider/venue/mapping, attempts and timestamps, duration, progress, reuse/recovery state, quota and retry data, raw and normalized digests, revision identifiers, source attribution, findings, remediation, and safety boundaries.

### Failure acceptance — resolved deterministically

Quota, provider outage, corrupt JSON, structurally invalid response, partial data, stale data, cancellation, and recovery are exercised through deterministic injected transports and persisted local evidence in the hosted test suite. Public provider failures are not triggered manually on demand because doing so is unreliable and could violate provider expectations. The manual guide identifies the exact focused tests as the retained acceptance evidence and documents operator recovery.

### Documentation and traceability — resolved

The canonical manual-testing guide covers U9 happy path, bounded ranges, mapping, lifecycle, degraded outcomes, correction lineage, U8 handoff, and workspace discovery. `docs/milestones/u9/traceability.md` maps requirements to implementation, tests, and retained evidence. `.osca/` is ignored. The exit review and OpenSpec task status are reconciled.

### Workspace discovers the complete evidence chain — resolved automatically

`test_workspace_discovers_complete_u9_evidence_chain` proves recursive discovery of:

- the canonical dataset revision;
- historical-acquisition evidence;
- persisted acquisition-job evidence;
- the U8 pipeline manifest;
- experiment and diagnostic artifacts;
- validation artifacts when diagnostic eligibility permits them.

It also confirms the workspace remains read-only with network, credential, recommendation, promotion, broker, and real-capital capabilities disabled. A final clean-profile `--snapshot` remains the only manual evidence item pending after the v2 contract upgrade.

## Inherited and deferred boundaries

- Kraken requires no credentials. Existing P13 secret and HTTPS boundaries remain authoritative; any future credentialed provider must add provider-specific canary coverage before admission.
- Dedicated acquisition, experiment, diagnostic, and validation workspace sections and detail pages remain U10 scope. U9 requires complete recursive discovery, not the U10 presentation model.
- A diagnostic-not-eligible U8 result is valid; U9 requires compatibility and fail-closed behavior, not predictive success.
- No recommendation, live serving, automatic promotion, broker/exchange connectivity, autonomous execution, external redistribution, or real-capital order path is enabled.

## Current decision

All previously material implementation and automated-validation gaps are resolved. U9 can close after the latest hosted Quality run is fully green and the operator retains one clean-profile workspace snapshot confirming the existing real evidence chain under the final v2 contract.
