# U9 Full Conformance Audit

- **Audit date:** 2026-08-02
- **Milestone:** U9 governed no-cost historical data acquisition
- **Implementation PR:** #72
- **Decision:** Not yet spec-complete

## Evidence reviewed

The audit reviewed the merged U9 planning authority from PR #70, the U9 foundation from PR #71, the complete PR #72 diff, hosted Quality results, the real Kraken clean-profile acquisition, the blocked Twelve Data equity result, and the retained U8 pipeline manifest.

Verified evidence includes:

- Kraken acquisition status `succeeded`;
- dataset revision `dee68bf2-e8e1-5521-9e93-d2d6dc606bae`;
- 720 canonical OHLCV rows;
- immutable raw payload and SHA-256 lineage;
- parser identity `kraken-ohlc-v1`;
- U8 run `d2cfcf58-ce0d-4bf9-be04-62ed84abb61d`;
- expected fail-closed diagnostic outcome `diagnostic_not_eligible`;
- explicit blocked-equity outcome for Twelve Data;
- all recommendation, promotion, broker, and real-capital boundaries disabled;
- hosted Ruff, strict mypy, pytest, OpenSpec, document-link, architecture, and secret-scan checks green before the final audit commits.

## Fully satisfied areas

- Primary `osca historical-data fetch` command exists and is discoverable.
- Network access requires explicit opt-in.
- Kraken public spot OHLC is the only admitted live historical source.
- Equity acquisition fails closed when no provider passes the policy gate.
- Governed CSV import remains available as the provider-independent fallback.
- Raw Kraken payloads and digests are retained.
- The current uncommitted Kraken bar is excluded.
- Canonical OHLCV validation and immutable revision persistence use the existing local import service.
- Equivalent completed requests are durably reused while canonical artifacts remain present.
- Equivalent in-process concurrent requests share one retrieval.
- Parser-version changes participate in revision identity.
- Rate-limit and service-unavailable provider responses receive retry guidance.
- Malformed payloads do not create accepted canonical revisions.
- CSV and network acquisition produce compatible canonical rows.
- Acquired revisions are accepted by the U8 research pipeline.
- The read-only analyst workspace recursively discovers the dataset, historical-acquisition evidence, manifest, experiment, and diagnostic artifacts; a focused regression test now proves this chain.
- `.osca/` is ignored by Git to prevent local evidence, databases, and provider payloads from being committed accidentally.

## Material gaps against the accepted OpenSpec

### 1. Canonical bounded request

The accepted specification requires bounded start and end ranges, freshness/completeness expectations, provider constraints, venue context where required, and canonical instrument identity or verified mapping. The current request exposes symbol, asset class, timeframe, optional Kraken `since`, and storage root only.

Missing:

- explicit start and end range;
- freshness and completeness expectations;
- verified instrument/venue mapping evidence;
- structured unsupported range and mapping outcomes.

### 2. Durable job lifecycle

The accepted specification requires stable progress, retry, cancellation, restart, and recovery behavior. The current implementation provides completed-result reuse and in-process locking but is not a persisted job lifecycle.

Missing:

- durable job state and correlation identity;
- progress reporting;
- cancellation;
- restart/recovery after process interruption;
- accepted behavior for partial retrieval after shutdown or timeout.

### 3. Complete degraded-outcome taxonomy

The accepted specification distinguishes fresh, stale, partial, invalid, corrupt, unavailable, refreshing, quota-blocked, credential-blocked, and policy-blocked outcomes. The implementation currently exposes succeeded, failed, provider-unavailable, and policy-blocked, with quota represented as provider-unavailable plus findings.

Missing:

- explicit quota-blocked status;
- stale, partial, corrupt, refreshing, and credential-blocked states;
- stable machine-readable remediation and retry metadata for each state.

### 4. Provider correction lineage

Parser changes create a new revision, but provider correction and normalization-build lineage are not explicitly linked to prior evidence.

Missing:

- predecessor/supersession relation;
- normalized digest in acquisition evidence;
- provider correction identity and rationale;
- build or normalization version separate from parser version.

### 5. Audit, telemetry, and attempts

The retained P13 evidence contains provider-request information, but the U9 acquisition evidence does not yet provide the complete accepted audit contract.

Missing or incomplete:

- stable acquisition request identity in the final U9 evidence;
- correlation identity across acquisition, ingestion, canonical revision, and U8 handoff;
- structured attempt history and timestamps;
- quota state and retry-after metadata;
- explicit normalized digest;
- telemetry for success, failure, duration, rows, retries, and reuse.

### 6. Manual failure acceptance

Automated tests cover malformed and quota/service cases, but the accepted task plan also requires manual outage/quota and malformed-response exercises with retained interpretation.

Missing:

- retained clean-profile manual outage/quota evidence;
- retained malformed-response manual evidence;
- operator-facing recovery confirmation.

### 7. Documentation and traceability closure

The U9 milestone and exit review are updated, but the accepted task package requires broader documentation and traceability reconciliation.

Missing or incomplete:

- canonical manual-testing guide updated with final U9 commands and evidence;
- root README current-state reconciliation after U9 completion;
- requirement/spec/test/implementation traceability update;
- troubleshooting for quota, outage, malformed response, parser revision, and reusable evidence;
- accepted OpenSpec task checklist reconciled with actual completion/deferment.

## Non-blocking or inherited coverage

- Secret-value canary coverage is not directly exercised by Kraken because the admitted endpoint is public and requires no credential. Existing production-ingestion secret boundaries remain applicable; a credentialed historical provider must add explicit canary coverage before admission.
- The current workspace presents U9 artifacts in the generic reports section. Dedicated acquisition, experiment, diagnostic, and validation sections remain U10 scope and are not required to prove basic U9 discovery.
- The diagnostic-not-eligible U8 outcome is valid and expected; U9 requires compatibility and fail-closed behavior, not successful model validation.

## Required path to U9 closure

Before U9 can be marked complete, either implement the material gaps above or explicitly amend the accepted U9 OpenSpec to defer them with rationale and ownership. Silent scope reduction is not acceptable.

Recommended completion slices:

1. Add canonical range/mapping contracts and structured outcome taxonomy.
2. Add persisted acquisition jobs with progress, cancellation, restart, attempt history, and correlation IDs.
3. Add complete lineage, normalized digest, correction/supersession relations, audit, and telemetry.
4. Add manual outage/quota/malformed acceptance and operator troubleshooting.
5. Reconcile manual-testing, README, traceability, and OpenSpec task status.
6. Re-run the full hosted Quality suite and update the exit decision.

## Current decision

PR #72 is a strong functional slice and the real clean-profile happy path is validated. It is not yet sufficient to close U9 under the accepted specification. Keep the PR in draft until the remaining requirements are implemented or formally deferred through an approved specification change.
