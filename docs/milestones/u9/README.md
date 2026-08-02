# U9 Governed No-Cost Historical Data Acquisition

- **Status:** Ready for implementation
- **Predecessor:** U8 real-world workflow reconciliation
- **Roadmap:** [U9-U14 usable release roadmap](../usable-release-roadmap.md)

## Intent

Allow a new local OSCA user to acquire sufficient historical equity and cryptocurrency data for the principal research demonstration without a paid account or an external preparation script, while preserving licensing, provenance, canonical identity, quality, revision, and safety controls.

## Governing requirements

- REQ-0021 canonical instrument identity
- REQ-0023 explicit provider mapping
- REQ-0024 ambiguity protection
- REQ-0025 provider capability contract
- REQ-0026 capability routing
- REQ-0027 visible provider transitions
- REQ-0028 licensing enforcement
- REQ-0029 named provider credentials
- REQ-0030 versioned daily bar contract
- REQ-0031 source immutability and retention evidence
- REQ-0032 canonical revisioning
- REQ-0033 typed dataset metadata
- REQ-0034 explicit retrieval requirements
- REQ-0035 structured resolution status
- REQ-0036 idempotent durable retrieval
- REQ-0037 gap detection and targeted repair
- REQ-0038 initial quality rules
- REQ-0041 approved interval set
- REQ-0042 UTC interval windows
- Universal evidence-based milestone exit gate

## Product outcome

The primary CLI provides a discoverable acquisition command that can:

1. Resolve a canonical instrument and provider mapping.
2. Validate provider capability, terms, authentication, quota, interval, and date range before retrieval.
3. Retrieve one no-cost equity source and Kraken spot market data.
4. Normalize data through the existing canonical OHLCV path.
5. Produce an immutable dataset revision with complete provenance, policy, integrity, and quality evidence.
6. Return actionable structured outcomes for unavailable, quota-blocked, policy-blocked, invalid, partial, or corrupt retrievals.
7. Feed the retained dataset directly into the U8 guided research pipeline.

## Required command surface

The implementation should expose the capability through the primary `osca` CLI. The provisional shape is:

```bash
uv run osca historical-data fetch AAPL \
  --asset-class equity \
  --timeframe 1d \
  --start 2021-08-01 \
  --end 2026-07-31 \
  --storage-root .osca/manual-test
```

The exact command hierarchy may change during design only if the same discoverability, compatibility, and acceptance outcomes are preserved.

## Provider admission gate

A provider path is not implementation-ready until the repository records:

- provider and endpoint identity;
- supported asset classes, venues, symbols, intervals, and history limits;
- authentication and credential requirements;
- free-tier or public-use limits;
- attribution requirements;
- retrieval, retention, transformation, export, backup, and redistribution policy;
- timestamp, adjustment, completion, and quality semantics;
- quota and retry behavior;
- raw-payload retention or explicit non-retention evidence;
- health and capability failure behavior;
- golden fixtures and conformance tests.

Licensing or terms uncertainty blocks admission. Convenience alone is not sufficient.

## Equity source decision gate

Kraken is already the approved cryptocurrency source. The no-cost equity source must be selected only after exact current licensing, account, quota, historical-depth, adjustment, and retention evidence is captured. If no candidate satisfies the gate, U9 must still deliver the canonical command, provider-neutral workflow, and CSV fallback while marking live equity acquisition blocked rather than silently using an ungoverned source.

## Functional scenarios

### Successful no-cost acquisition

Given an admitted provider capability and a valid canonical request, OSCA retrieves, validates, normalizes, stores, and returns a dataset revision with complete lineage and no unsafe side effects.

### Offline CSV fallback

Given no usable network provider, the existing local CSV import remains available and produces equivalent canonical revision and quality evidence.

### Unsupported capability

An unsupported asset, interval, range, or venue fails before network retrieval with a structured capability explanation.

### Quota or provider outage

Quota exhaustion, rate limiting, timeout, or provider outage returns an explicit retryable or blocked outcome and does not replace an accepted revision with partial data.

### Policy uncertainty

Missing or uncertain terms metadata fails closed before retrieval or retention.

### Malformed or low-quality response

Malformed observations, invalid OHLC relationships, duplicates, non-finite values, negative volume, identity/time inconsistencies, or range gaps produce visible findings and cannot silently enter accepted canonical history.

### Repeated request

Equivalent concurrent or repeated retrieval requests share or reuse durable work and do not create ambiguous duplicate revisions.

### Correction or parser change

Provider corrections or normalization changes create a new identifiable revision and preserve prior accepted evidence.

## Security and safety

- Credentials use named secret references and never enter logs, URLs, manifests, payload exports, or portable configuration.
- Network access is limited to admitted provider endpoints.
- No recommendation, model promotion, broker, exchange-order, autonomous-execution, or real-capital capability is introduced.
- Acquisition output is research data, not investment advice.

## Observability and evidence

Retain, as policy permits:

- canonical request identity;
- provider capability snapshot;
- provider mapping identity;
- retrieval timestamps and attempt status;
- HTTP/status class without secrets;
- quota and retry evidence;
- raw response digest or intentional non-retention record;
- parser/build identity;
- normalized payload digest and path;
- dataset revision ID;
- licensing/retention decision;
- quality findings;
- correlation and job identities;
- final structured outcome.

## Compatibility and migration

- Existing CSV import and provider module entry points remain compatible unless an explicit deprecation is documented and tested.
- Existing stored revisions require no destructive migration.
- New metadata fields must be versioned and backward-readable or safely reported as unavailable.

## Validation

Automated validation must include:

- provider capability and policy contract tests;
- golden-response normalization tests;
- secret-exclusion tests;
- quota, timeout, malformed-response, and unsupported-capability tests;
- idempotency and concurrent-request tests;
- revision and correction tests;
- CLI help and structured-output tests;
- end-to-end Kraken acquisition through canonical storage;
- end-to-end admitted equity acquisition when terms evidence permits it;
- CSV fallback equivalence;
- U8 pipeline compatibility;
- workspace discovery of the resulting dataset.

## Manual acceptance

On a clean local profile:

1. Run `osca doctor` or the current equivalent.
2. Acquire or import AAPL daily history.
3. Acquire one Kraken spot pair.
4. Inspect dataset metadata, provenance, policy, integrity, and quality findings.
5. Run the U8 research pipeline against one acquired revision.
6. Open the workspace and confirm discovery.
7. Exercise one provider outage or quota-blocked path.
8. Confirm all recommendation and execution boundaries remain disabled.

## Exit criteria

U9 is complete only when:

- at least one no-cost cryptocurrency acquisition path passes;
- one no-cost equity path passes, or is explicitly blocked with retained terms evidence and the provider-neutral/CSV workflow remains complete;
- primary CLI discovery and documentation match behavior;
- canonical provenance, policy, revision, integrity, and quality evidence is retained;
- failure paths are actionable and non-corrupting;
- U8 accepts the resulting revision;
- automated and manual evidence is retained;
- all hosted quality gates pass.
