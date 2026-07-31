# p10-runtime-provider-routing Specification

## Purpose

Define capability-based runtime source selection that preserves explicit provenance and fails closed when a source is stale, blocked, or unavailable.

## Requirements

### Requirement: Capability-based source selection

P10 SHALL route supported requests by capability and SHALL NOT require FRED or silently substitute one capability for another.

#### Scenario: Governed local OHLCV is selected
- **GIVEN** an OHLCV request with an explicit existing governed Parquet payload
- **WHEN** runtime routing is evaluated
- **THEN** the local OHLCV source is selected with payload provenance and network access remains unused.

#### Scenario: SEC fixture is selected before live preview
- **GIVEN** a company-facts or filings request with an explicit SEC fixture
- **WHEN** runtime routing is evaluated
- **THEN** fixture evidence is selected without network access and no live source is blended into the decision.

#### Scenario: SEC source is not explicit
- **GIVEN** a company-facts or filings request without a fixture and without explicit live-preview enablement
- **WHEN** runtime routing is evaluated
- **THEN** the decision is `provider_unavailable`.

### Requirement: Stale evidence remains explicit

P10 SHALL identify stale selectable evidence and SHALL fail closed unless the caller explicitly allows stale use.

#### Scenario: Stale evidence is not allowed
- **GIVEN** an available source older than the request's maximum age
- **WHEN** stale use is not enabled
- **THEN** the decision is `provider_unavailable` and no payload is selected.

#### Scenario: Stale evidence is explicitly allowed
- **GIVEN** an available source older than the request's maximum age
- **WHEN** stale use is enabled
- **THEN** the source is selected with `stale: true` and a stale-source finding.

### Requirement: Macro routing is optional and fail closed

P10 SHALL NOT make OSCA depend on FRED or any other macro provider.

#### Scenario: FRED macro request is evaluated
- **GIVEN** a macro-series request whose preferred or default provider is FRED
- **WHEN** runtime routing is evaluated
- **THEN** the decision is `policy_blocked`, network access is unused, no credential is materialized, and no payload is exposed.

#### Scenario: Unconfigured macro provider is requested
- **GIVEN** a macro-series request for a provider that is not enabled
- **WHEN** runtime routing is evaluated
- **THEN** the decision is `provider_unavailable`.

### Requirement: Macro failure does not stop non-macro work

P10 SHALL retain successful non-macro decisions when a batch also contains blocked or unavailable macro requests.

#### Scenario: Mixed local and macro batch
- **GIVEN** a selectable local OHLCV request and a FRED macro request
- **WHEN** the requests are routed as one batch
- **THEN** the batch outcome is `partial`, the OHLCV decision remains selected, the macro decision remains policy-blocked, and `non_macro_continued` is true.

### Requirement: Routing evidence is inspectable

P10 SHALL expose API and CLI surfaces for routing decisions and the capability policy matrix.

#### Scenario: Operator inspects routing policy
- **GIVEN** the P10 module CLI
- **WHEN** the operator runs the policy command
- **THEN** OSCA reports source precedence and missing-source status for OHLCV, company facts, filings, and macro series.

### Requirement: Deferred boundaries remain disabled

P10 SHALL preserve production-ingestion, recommendation, broker, autonomous-execution, and real-capital boundaries.

#### Scenario: A routing decision is produced
- **GIVEN** any selected, blocked, or unavailable decision
- **WHEN** its evidence is inspected
- **THEN** credential materialization, production ingestion, recommendations, and real-capital orders remain disabled.

### Requirement: P10 evidence retention

P10 SHALL retain requirements, traceability, OpenSpec, manual-testing review, automated validation, and hosted Quality evidence.

#### Scenario: P10 completion is requested
- **GIVEN** P10 implementation work
- **WHEN** completion is evaluated
- **THEN** exit review evidence identifies implemented, fixture-backed, optional-preview, policy-blocked, unavailable, stale, partial, and deferred behavior.
