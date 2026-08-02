# Design: U9 Governed Historical Acquisition

## Architecture

The acquisition workflow is an application capability owned by market-data retrieval. CLI and future API adapters invoke the same application service. Provider adapters remain behind provider contracts and may not write canonical storage directly.

Dependency direction:

```text
CLI/API adapter
  -> historical acquisition application service
     -> instrument registry and provider mapping
     -> provider capability/policy resolver
     -> provider adapter
     -> normalization and quality validation
     -> catalog/dataset revision persistence
     -> workflow, audit, and telemetry services
```

## Interaction classification

- Provider calls are external, bounded, authenticated only when the admitted capability requires it, and governed by timeout, quota, retry, and policy controls.
- Canonical persistence is local and capability-owned.
- Workspace and U8 pipeline integration are read-only consumers of retained dataset contracts.

## Persistence ownership

- Provider capability and policy metadata: provider-governance ownership.
- Instrument mappings: instrument-registry ownership.
- Retrieval job state: workflow ownership.
- Raw payload or non-retention evidence: market-data/catalog ownership under provider policy.
- Canonical Parquet payload and SQLite metadata: existing market-data storage ownership.
- Audit and telemetry: operations ownership.

No provider adapter owns or mutates canonical revisions.

## Public-contract impact

Introduce or extend versioned contracts for:

- historical acquisition request;
- provider admission/capability snapshot;
- acquisition outcome and structured resolution status;
- retrieval evidence and policy decision;
- CLI structured output.

Existing OHLCV, quality-finding, dataset-revision, provider-capability, job, and evidence contracts remain authoritative. Any new fields must be additive, versioned, and backward-readable or reported as unavailable.

## Provider admission

Kraken reuses its accepted capability and policy baseline, with U9-specific historical-range and evidence tests.

The equity provider remains blocked until exact current evidence establishes:

- permitted endpoint and use case;
- free/public account requirements;
- quota and historical-depth limits;
- symbol and venue semantics;
- timestamp, split/dividend adjustment, and completion semantics;
- raw-data retention and derived-data permissions;
- export, backup, redistribution, and attribution obligations.

Admission evidence is reviewed as product/provider governance, not inferred in adapter code.

## Request lifecycle

1. Parse and validate the canonical request.
2. Resolve canonical instrument and verified provider mapping.
3. Resolve provider capability and policy.
4. Reject unsupported or policy-blocked work before network access.
5. Create or join an idempotent durable retrieval job.
6. Retrieve with bounded timeout, retry, rate-limit, and cancellation handling.
7. Retain raw payload or explicit non-retention evidence as policy allows.
8. Parse and normalize into the canonical OHLCV contract.
9. Run deterministic quality and range validation.
10. Reject or quarantine invalid data; never overwrite accepted revisions.
11. Create a new immutable dataset revision when acceptance criteria pass.
12. Emit structured outcome, audit event, telemetry, and retained evidence.

## Failure behavior

- Unsupported capability: fail before network access.
- Missing/invalid credentials: fail with named-secret remediation and no secret disclosure.
- Terms uncertainty: fail closed.
- Quota/rate limit: return quota-blocked with retry metadata where available.
- Timeout/outage: return unavailable or retryable without accepting partial data.
- Malformed response: retain safe diagnostic evidence and reject acceptance.
- Partial range: report partial/gapped status; targeted repair may be scheduled but accepted history is preserved.
- Ambiguous mapping: quarantine before provider data enters canonical storage.
- Parser or provider correction: create a new revision with lineage.

## Security

- Allow only admitted HTTPS endpoints.
- Use named secret references through the security capability.
- Redact credentials and sensitive headers from logs, URLs, errors, evidence, and exports.
- Bound response size, timeout, retries, and parser resource use.
- Treat provider data as untrusted input.
- Preserve loopback-only workspace defaults and ADR-0044 execution boundaries.

## Observability

Emit correlated structured logs, metrics, traces, audit events, and job progress for:

- request validation;
- provider selection and policy decision;
- network attempts and classified outcomes;
- quota/rate-limit state;
- bytes/rows received without retaining prohibited content;
- parse and quality findings;
- revision creation or rejection;
- duration and retry counts;
- final structured status.

## Rollout

1. Land contracts and fixtures behind no live equity admission.
2. Implement provider-neutral service and CLI with CSV fallback and Kraken.
3. Admit equity only after governance evidence is reviewed.
4. Enable documented manual acceptance on a clean profile.

## Rollback and forward recovery

- The feature is additive; existing CSV import remains intact.
- Disable a provider capability without deleting accepted revisions.
- Preserve failed job/evidence records for diagnosis.
- Parser fixes create new revisions rather than mutating accepted history.
- If a new metadata field causes incompatibility, readers report unavailable/incompatible evidence and continue to preserve stored content.

## Architecture fitness

Add checks that:

- adapters do not import persistence implementations directly;
- provider modules cannot write canonical storage;
- CLI does not duplicate provider-policy or validation logic;
- secrets never enter portable contracts;
- recommendation and execution packages are not introduced as dependencies.
