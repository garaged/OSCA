# Data Sources, Credentials, Import, and Acquisition Delta Specification

## ADDED Requirements

### Requirement: Authoritative provider capability catalog

The desktop application SHALL derive provider status from canonical admission policy and SHALL represent admission, credential, network, profile, resource, and operational states separately.

#### Scenario: User opens Data Sources

- **WHEN** a user opens the Data Sources destination
- **THEN** every provider row shows admission, approved resources, credential mode, evidence date, rationale, and findings from canonical policy
- **AND** credential presence does not change admission
- **AND** approved Kraken public OHLC is distinguishable from needs-evidence and policy-blocked providers
- **AND** sample and governed local import remain visible no-cost offline paths.

### Requirement: OS-vault credential lifecycle

The desktop application SHALL store named credentials only through the Python `SecretVault` boundary and SHALL never return or ordinarily persist secret values.

#### Scenario: User stores and probes a credential

- **WHEN** a user submits a non-empty credential for a named-secret provider
- **THEN** Python stores it through the OS keyring-backed vault
- **AND** the frontend receives only a validated display reference and presence state
- **AND** the input is cleared after submission
- **AND** the value is absent from desktop state, profile files, SQLite, Parquet, logs, URLs, and evidence.

#### Scenario: Vault is unavailable

- **WHEN** the OS credential backend is unavailable or denied
- **THEN** the operation fails closed with safe remediation
- **AND** no plaintext fallback is created
- **AND** offline import and sample paths remain usable.

### Requirement: Credentials do not promote providers

The desktop application SHALL enforce provider admission independently of credential state.

#### Scenario: Credential exists for a needs-evidence provider

- **WHEN** a credential is present for Twelve Data or another needs-evidence provider
- **THEN** admission remains needs-evidence
- **AND** production acquisition remains unavailable
- **AND** promotion blockers remain visible
- **AND** no UI action automatically edits admission policy.

### Requirement: Governed offline local import

The desktop application SHALL delegate local OHLCV CSV validation and persistence to the canonical Python import service.

#### Scenario: User imports a valid CSV

- **WHEN** a user submits an absolute selected CSV path with symbol, timeframe, source, and calendar metadata
- **THEN** the import runs with no provider network or credential requirement
- **AND** canonical SQLite metadata and Parquet payload are retained
- **AND** provenance, row count, hashes, and dataset revision are returned
- **AND** React and Rust do not parse or persist the file.

#### Scenario: Local import is invalid

- **WHEN** the path or content is unsafe, malformed, incompatible, or unsupported
- **THEN** no success or dataset revision is claimed
- **AND** the typed error identifies remediation without raw stack traces
- **AND** existing accepted profile content remains safe.

### Requirement: Explicit governed Kraken acquisition

The desktop application SHALL expose approved Kraken public spot OHLC acquisition through the canonical historical-acquisition service with explicit request-scoped network consent.

#### Scenario: Network consent is absent

- **WHEN** a user configures a Kraken acquisition but does not explicitly enable networking for the request
- **THEN** no provider request is made
- **AND** submission remains blocked with clear guidance
- **AND** catalog, local import, credential, and evidence inspection remain offline.

#### Scenario: Kraken acquisition succeeds

- **WHEN** a user explicitly submits an approved Kraken crypto OHLC request
- **THEN** no credential is required
- **AND** bounded HTTPS retrieval, normalization, and canonical import are used
- **AND** retained job and acquisition evidence identify hashes, revisions, attribution, attempts, duration, findings, and safety flags
- **AND** internal-use-only and redistribution-disabled status are visible.

### Requirement: Acquisition lifecycle and distinct outcomes

The desktop application SHALL preserve canonical progress, cancellation, retry/reuse, recovery, and typed outcome semantics.

#### Scenario: Equivalent request is repeated

- **WHEN** a completed equivalent request is submitted again
- **THEN** canonical evidence may be reused according to idempotency rules
- **AND** the UI identifies reused rather than false new acquisition
- **AND** an equivalent canonical dataset is not silently duplicated.

#### Scenario: Acquisition fails or is cancelled

- **WHEN** the outcome is policy blocked, credential blocked, quota blocked, provider unavailable, partial, stale, invalid, corrupt, cancelled, or failed
- **THEN** the exact typed state remains visible
- **AND** findings and bounded remediation are shown
- **AND** retry is offered only when safe
- **AND** no completed dataset claim is made without retained evidence.

### Requirement: Accessible narrow data-source workflow

The D3 provider, credential, import, acquisition, job, evidence, warning, and confirmation surfaces SHALL remain responsive and keyboard/screen-reader operable.

#### Scenario: Keyboard-only user manages data sources

- **WHEN** a user operates D3 without a pointer at narrow or desktop width
- **THEN** navigation, provider actions, credential controls, import fields, request controls, progress, evidence, and confirmations are reachable
- **AND** page navigation and submitted errors move focus appropriately
- **AND** status is not communicated by color or motion alone
- **AND** secret values are never announced after submission.

### Requirement: Narrow provider authority and permanent safety

D3 SHALL preserve the single Rust `desktop_request` bridge and SHALL NOT add generic keychain, HTTP, file, shell, environment, SQLite, Parquet, recommendation, broker, exchange, autonomous, live-order, or real-capital authority.

#### Scenario: D3 architecture is inspected

- **WHEN** automated architecture tests inspect React and Rust
- **THEN** all provider, credential, import, and acquisition behavior enters Python through allowlisted versioned methods
- **AND** no generic native plugin or direct provider client is present
- **AND** recommendations and every execution capability remain unavailable.

### Requirement: Evidence-based D3 completion

D3 SHALL remain incomplete until specification, implementation, automated tests, OpenSpec, traceability, secret-redaction evidence, network-negative evidence, hosted validation, supported-platform manual acceptance, limitations, and exit review are retained.

#### Scenario: D3 exit is evaluated

- **WHEN** the D3 exit review is prepared
- **THEN** macOS ARM64 and Linux x86-64 acceptance has passed
- **AND** credential, policy, network, import, acquisition, accessibility, and safety defects are resolved or block exit
- **AND** no provider has been promoted without accepted evidence
- **AND** merge remains gated on explicit owner direction.
