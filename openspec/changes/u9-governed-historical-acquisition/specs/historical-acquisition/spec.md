# Historical Acquisition Delta Specification

## ADDED Requirements

### Requirement: Canonical historical acquisition request

OSCA SHALL accept a versioned historical acquisition request containing canonical instrument identity or resolvable user input, asset class, venue context where required, approved interval, bounded start/end range, freshness/completeness expectations, provider constraints, and storage target.

#### Scenario: Valid bounded request

- **WHEN** an operator submits a supported bounded request
- **THEN** OSCA creates a stable request identity and proceeds to capability and policy resolution.

#### Scenario: Invalid or unsupported request

- **WHEN** asset, interval, venue, range, or required context is invalid or unsupported
- **THEN** OSCA rejects the request before network access with a structured actionable explanation.

### Requirement: Provider admission and policy gate

OSCA SHALL retrieve historical data only through a provider capability whose current authentication, quota, licensing, attribution, retention, transformation, export, backup, redistribution, timestamp, adjustment, quality, and health behavior is explicitly recorded and accepted for the requested use.

#### Scenario: Admitted provider

- **WHEN** the provider capability and request satisfy the recorded policy
- **THEN** retrieval may proceed and the capability/policy snapshot is retained with the result.

#### Scenario: Missing or uncertain policy

- **WHEN** required terms or capability evidence is missing, stale, conflicting, or uncertain
- **THEN** OSCA fails closed before retrieval or retention and records a policy-blocked outcome.

### Requirement: No-cost principal workflow

OSCA SHALL provide a principal historical-data workflow that does not require a paid provider account, using an admitted no-cost equity path, Kraken public market data, and local CSV import as the provider-independent fallback.

#### Scenario: No-cost crypto acquisition

- **WHEN** an operator requests a supported Kraken spot pair and range
- **THEN** OSCA retrieves and normalizes the data without requiring a paid account.

#### Scenario: Equity source not admitted

- **WHEN** no equity candidate satisfies the provider admission gate
- **THEN** OSCA exposes the equity path as policy-blocked, preserves the provider-neutral command and CSV fallback, and does not silently adopt an ungoverned source.

### Requirement: Canonical normalization and revision

OSCA SHALL parse provider responses as untrusted input, normalize accepted observations through the existing canonical OHLCV contract, run deterministic quality validation, and create an immutable identifiable dataset revision rather than allowing provider adapters to write or mutate canonical storage directly.

#### Scenario: Valid response

- **WHEN** retrieved observations pass identity, interval, range, OHLC, volume, finiteness, duplication, timestamp, and gap rules
- **THEN** OSCA creates a canonical dataset revision with complete lineage and integrity metadata.

#### Scenario: Invalid or malformed response

- **WHEN** parsing or deterministic validation finds invalid, ambiguous, corrupt, or policy-incompatible data
- **THEN** OSCA rejects or quarantines the result, retains safe findings, and leaves accepted revisions unchanged.

#### Scenario: Provider correction or parser change

- **WHEN** accepted history is reprocessed because of provider correction, parser change, or normalization change
- **THEN** OSCA creates a new revision linked to prior evidence and does not silently rewrite history.

### Requirement: Durable idempotent retrieval

OSCA SHALL execute equivalent concurrent or repeated acquisition requests as durable idempotent work with stable status, progress, retry, cancellation, and restart behavior.

#### Scenario: Equivalent concurrent requests

- **WHEN** equivalent requests overlap
- **THEN** OSCA joins or reuses the same durable work and avoids ambiguous duplicate revisions.

#### Scenario: Interrupted retrieval

- **WHEN** retrieval is interrupted by cancellation, shutdown, timeout, or transient outage
- **THEN** OSCA records the classified outcome and can retry or recover without accepting partial corrupt data.

### Requirement: Explicit degraded outcomes

OSCA SHALL distinguish successful, fresh, stale, partial, invalid, corrupt, unavailable, refreshing, quota-blocked, credential-blocked, and policy-blocked outcomes and provide safe remediation.

#### Scenario: Quota exhausted

- **WHEN** the provider reports rate limiting or quota exhaustion
- **THEN** OSCA returns quota-blocked status, retains retry metadata where permitted, and preserves accepted data.

#### Scenario: Provider unavailable

- **WHEN** timeout, DNS, transport, server, or health failure prevents retrieval
- **THEN** OSCA returns unavailable or retryable status without silently substituting or merging another provider series.

### Requirement: Acquisition evidence

OSCA SHALL retain policy-permitted evidence sufficient to reproduce and audit an acquisition, including request identity, provider capability and mapping, retrieval attempts, timestamps, quota state, raw-response digest or intentional non-retention record, parser/build identity, normalized digest, dataset revision, policy decision, quality findings, correlation identity, and final outcome.

#### Scenario: Raw retention prohibited

- **WHEN** provider policy prohibits raw-payload retention
- **THEN** OSCA retains an explicit non-retention record and the permitted request, digest, parser, policy, and normalized-lineage evidence.

#### Scenario: Evidence inspection

- **WHEN** an operator inspects an acquired dataset
- **THEN** the dataset exposes its upstream request, provider, policy, integrity, quality, and revision lineage without exposing secrets.

### Requirement: Secret and endpoint safety

OSCA SHALL use named secret references for provider credentials, restrict network access to admitted encrypted endpoints, bound timeout/retry/response resources, and exclude secrets from logs, URLs, errors, manifests, payload exports, and portable configuration.

#### Scenario: Credential required

- **WHEN** an admitted capability requires credentials
- **THEN** OSCA resolves a named secret through the security capability and never persists the secret value in acquisition evidence.

#### Scenario: Secret canary

- **WHEN** test credentials contain known canary values
- **THEN** no canary value appears in logs, errors, URLs, evidence, exports, or stored metadata.

### Requirement: Primary CLI and compatibility

OSCA SHALL expose historical acquisition through the primary `osca` CLI with discoverable help and structured outcomes while preserving the existing local CSV import workflow.

#### Scenario: CLI discovery

- **WHEN** an operator requests primary CLI help
- **THEN** historical acquisition, supported constraints, provider attribution, storage behavior, and fallback guidance are discoverable.

#### Scenario: U8 pipeline handoff

- **WHEN** acquisition creates an accepted dataset revision
- **THEN** the revision can be supplied directly to the U8 guided research pipeline without manual data conversion.

### Requirement: Execution boundary preservation

OSCA SHALL treat acquired data as research evidence only and SHALL NOT enable recommendations, live model serving, automatic promotion, broker/exchange order connectivity, autonomous execution, or real-capital orders.

#### Scenario: Successful acquisition

- **WHEN** acquisition succeeds
- **THEN** all recommendation and execution capability flags remain disabled and no order or recommendation side effect occurs.
