# Requirements Catalog

- **Status:** Active baseline catalog
- **Governing role:** Product authority
- **Purpose:** Assign stable identifiers and engineering metadata to testable requirements derived without semantic change from the approved PRD and active decisions.
- **Authoritative sources:** [Product requirements](../product-requirements.md), [decision log](../decision-log.md), [ADR-0001](../decisions/ADR-0001-requirements-authority-and-traceability-model.md)
- **Downstream consumers:** Milestone intents, specifications, acceptance criteria, tests, documentation, risk treatments, and automated traceability checks

## Authority

This catalog is an index and decomposition of authoritative requirements. It does not replace the PRD or active accepted decisions and cannot change their meaning.

If a catalog entry conflicts with its cited source, the cited source governs and the catalog entry must be corrected. A proposed correction that changes product meaning requires product decision governance.

## Identifier policy

Requirements receive immutable identifiers in the form `REQ-NNNN`.

The numeric identifier carries no domain or milestone meaning. Classification and allocation are stored as metadata so a requirement can move between modules or milestones without changing identity.

Identifiers are never reused. A retired or superseded requirement remains in the catalog with its history and replacement reference.

## Required fields

Each catalog entry must contain:

| Field | Meaning |
|---|---|
| ID | Stable `REQ-NNNN` identifier |
| Title | Short unique description |
| Normative statement | Atomic, testable requirement using defined requirement language |
| Authority | Exact PRD section and applicable decision IDs |
| Classification | Product behavior, architecture constraint, quality attribute, security, process, documentation, or governance |
| Scope | Affected capability or cross-cutting concern |
| Planned milestones | Milestones expected to specify or satisfy the requirement |
| Verification class | Test, analysis, inspection, demonstration, or mixed |
| Risk links | Related risk identifiers |
| Status | Active, superseded, retired, or deferred |
| Supersedes / superseded by | Requirement-history links |
| Notes | Non-normative clarification only |

## Decomposition rules

- Each normative statement expresses one independently verifiable obligation where practical.
- Decomposition may make implicit subjects or conditions explicit but cannot add behavior.
- Requirement language follows the approved PRD definitions.
- A requirement may cite multiple PRD passages and decisions.
- A PRD passage may produce multiple catalog requirements when it contains separable obligations.
- Duplicate requirements are consolidated while preserving all authority links.
- Implementation details are excluded unless already mandated by an authoritative source.
- Unresolved design questions are not converted into requirements.

## Population status

The catalog policy is accepted. Exact numbered requirements are extracted and reviewed when a milestone selects their scope, keeping decomposition small and reviewable. ADR-0001 requires the selected entries and machine-validatable links before implementation depends on them.

## Catalog entries

The following entries are approved for M1 and are authoritative decompositions of their cited product sources.

| ID | Title | Normative statement | Authority | Classification | Scope | Milestone | Verification | Risk links | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-0001 | Runnable local product | OSCA must run locally as one coherent minimal product using the single-user modular-monolith topology. | PRD M1; D-006; D-007 | Product behavior | Cross-cutting | M1 | Demonstration, test | Architecture drift | Active |
| REQ-0002 | Shared application behavior | Web, API, and CLI clients must invoke shared application capabilities and must not duplicate authoritative business or security rules. | PRD 16.2, 16.6; D-021 | Architecture constraint | Interfaces | M1 | Structural, contract | Interface divergence | Active |
| REQ-0003 | Web readiness shell | The web shell must expose the M1 system-readiness outcome as OSCA's primary interactive surface. | PRD 16.1; PRD M1 | Product behavior | Web adapter | M1 | End-to-end, accessibility | User effectiveness | Active |
| REQ-0004 | Versioned readiness API | OSCA must expose the readiness capability through an explicitly versioned application API with structured validation and errors. | PRD 16.2, 16.6; PRD M1 | Product behavior | API adapter | M1 | Contract, end-to-end | Compatibility | Active |
| REQ-0005 | Readiness CLI | OSCA must expose readiness, diagnostic-job, configuration, backup, and restore operations through the CLI where included in M1 scope. | PRD 16.3; PRD M1 | Product behavior | CLI adapter | M1 | Contract, end-to-end | Automation reliability | Active |
| REQ-0006 | Loopback-safe local profile | Local-only mode must bind to loopback or a protected local channel by default and rely on the operating-system user boundary. | PRD 26.1; D-031 | Security | Security/configuration | M1 | Security-negative, integration | Unsafe exposure | Active |
| REQ-0007 | Explicit network exposure | Binding to a non-local interface must require explicit configuration, and unsafe remote exposure must be rejected where practical. | PRD 26.1; D-031 | Security | Security/configuration | M1 | Security-negative | Unsafe exposure | Active |
| REQ-0008 | Protected remote profile | The personal-server configuration skeleton must require authenticated sessions and authenticated encrypted transport for protected remote operations. | PRD 26.1, 26.3; D-031; D-032 | Security | Security/transport | M1 | Analysis, security-negative | Identity and transport compromise | Active |
| REQ-0009 | Vault-backed secret abstraction | Credentials must use an operating-system credential store or replaceable encrypted secret-vault adapter, and consumers must use named secret references rather than secret values. | PRD 26.2; D-031 | Security | Secrets | M1 | Component, security-negative | Secret disclosure | Active |
| REQ-0010 | Secret exclusion | Secrets must not appear in logs, errors, URLs, manifests, ordinary backups, exported configuration, or diagnostic bundles. | PRD 26.2, 28.4 | Security | Cross-cutting | M1 | Security-negative, inspection | Secret disclosure | Active |
| REQ-0011 | Durable job identity | Every M1 diagnostic job and run must have a stable typed identity and expose durable status and progress. | PRD 16.2, 29.2; D-036 | Product behavior | Workflow | M1 | Component, contract | Lost or ambiguous work | Active |
| REQ-0012 | Durable job lifecycle | The diagnostic job must define inputs, outputs, idempotency, concurrency, checkpoint, retry, cancellation, safe shutdown, and restart/resume behavior. | PRD 29.2, 29.3; D-036 | Quality attribute | Workflow | M1 | Component, failure, recovery | Workflow corruption | Active |
| REQ-0013 | Typed metadata identity | Retained M1 job, configuration, and backup records must have stable typed identity, schema/revision, timestamps, producer/build identity, lineage, integrity, and availability metadata as applicable. | PRD 11, 13.5; PRD M1 | Product behavior | Catalog | M1 | Schema, component | Provenance loss | Active |
| REQ-0014 | Structured correlated telemetry | M1 behavior must emit structured logs, metrics, traces, job events, and distinct audit records connected by correlation identities. | PRD 28.2, 28.4; D-035 | Quality attribute | Operations | M1 | Component, observability | Undiagnosable failure | Active |
| REQ-0015 | Built-in health | The built-in readiness experience must distinguish healthy, degraded, blocked, recovering, and unavailable states and provide impact and remediation guidance. | PRD 28.1; D-035 | Product behavior | Operations | M1 | Component, end-to-end | Silent failure | Active |
| REQ-0016 | Configuration validation | OSCA must validate configuration before serving or running affected work and return actionable structured diagnostics for invalid or unsafe combinations. | PRD M1; PRD 26.1, 26.3 | Security | Configuration | M1 | Unit, property, security-negative | Misconfiguration | Active |
| REQ-0017 | Minimal protected backup | M1 must create a consistent minimal backup containing required configuration references, metadata, job state, manifests, and audit metadata while excluding secrets and transient content. | PRD 27.1, 27.2; PRD M1 | Product behavior | Recovery | M1 | Component, integration | State loss, secret disclosure | Active |
| REQ-0018 | Verified isolated restore | M1 restore must verify integrity and compatibility, preview impact, restore into an isolated location, and leave active state unchanged until validation succeeds. | PRD 27.3, 27.5; PRD M1 | Product behavior | Recovery | M1 | Recovery, security-negative | Corrupt or unsafe restore | Active |
| REQ-0019 | Version-matched executable documentation | M1 installation, configuration, security, interface, job, backup/restore, and troubleshooting documentation must match the product version, and executable examples must be automatically validated where practical. | PRD 17; D-022; PRD M1 | Documentation | Cross-cutting | M1 | Inspection, executable example | Documentation drift | Active |
| REQ-0020 | Evidence-based completion | M1 behavior is complete only when requirements, specifications, acceptance criteria, implementation, verification, documentation, observability, failure behavior, and residual risks are traceably evidenced. | PRD 38; universal milestone exit gate; D-042; D-046 | Governance | Cross-cutting | M1 | Traceability audit | False completion | Active |

Detailed supersession fields and notes are empty for these initial entries. No identifier may be reused if an entry is rejected or retired.


## M2 catalog entries

The following entries are accepted authoritative decompositions for M2. Product authority approved the M2 intent and allocation on 2026-07-18.

| ID | Title | Normative statement | Authority | Classification | Scope | Milestone | Verification | Risk links | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-0021 | Canonical instrument identity | OSCA must assign provider-neutral stable identities to supported stocks and spot-cryptocurrency pairs; displayed tickers and provider symbols must not be primary identity. | PRD 8.3; D-012 | Product behavior | Instrument | M2 | Schema, property, component | Symbol ambiguity | Active |
| REQ-0022 | Extensible registration | A local owner must be able to discover or manually register an instrument within a supported asset class without changing application code. | PRD 8.2; D-012; PRD M2 | Product behavior | Instrument/interfaces | M2 | Contract, end-to-end | Registration error | Active |
| REQ-0023 | Explicit provider mapping | Every provider mapping must identify canonical instrument, provider identifier/symbol, scope, venue context, validity, provenance, verification, and capabilities. | PRD 8.4; D-012 | Product behavior | Instrument/provider | M2 | Schema, component | Mapping corruption | Active |
| REQ-0024 | Ambiguity protection | Ambiguous, duplicate, conflicting, expired, or unverified mappings must be rejected or quarantined before provider data enters canonical storage. | PRD 8.2–8.4; D-012 | Data integrity | Instrument | M2 | Property, security-negative | Canonical corruption | Active |
| REQ-0025 | Provider capability contract | An adapter must publish machine-readable asset, venue, interval, history, freshness, adjustment/timestamp, authentication, quota, licensing, quality, and health limitations. | PRD 12.2; D-016; D-040 | Contract | Provider | M2 | Contract, adapter conformance | Provider change | Active |
| REQ-0026 | Capability routing | Daily-data requests must use an explicit capability-specific ordered provider policy considering support, freshness, quality, quota, licensing, cost, and user preference. | PRD 12.1; D-016 | Product behavior | Provider routing | M2 | Component, property | Wrong-provider selection | Active |
| REQ-0027 | Visible provider transitions | Fallback or provider transition must remain explicit in provenance and must not silently extend or merge a canonical series. | PRD 12.3; D-016 | Data integrity | Provider/data | M2 | Contract, property | Silent data mixing | Active |
| REQ-0028 | Licensing enforcement | Provider policy metadata must govern retrieval, retention, transformation, export, backup, and redistribution; uncertainty must fail closed. | PRD 12.2, 13.1, 37; D-040 | Licensing/security | Provider/data | M2 | Policy, security-negative | License violation | Active |
| REQ-0029 | Named provider credentials | Provider consumers must use named secret references through the Security capability, and credentials must not enter portable configuration, payloads, logs, URLs, evidence, or exports. | PRD 12.2, 26.2; D-040 | Security | Provider | M2 | Adapter, secret canary | Secret disclosure | Active |
| REQ-0030 | Versioned daily bar contract | M2 must define a versioned daily OHLCV observation with canonical instrument identity, interval, timestamp semantics, units/currencies, completion state, provider provenance, and integrity. | PRD 10, 13.2; D-013, D-017 | Contract | Market Data | M2 | Schema, golden fixture | Semantic corruption | Active |
| REQ-0031 | Source immutability and retention evidence | Permitted retained source payloads must be immutable and checksummed; intentional non-retention must be recorded with provider, request, retrieval, parser, and policy metadata. | PRD 13.1; D-017, D-040 | Data integrity/licensing | Market Data | M2 | Component, inspection | Provenance loss | Active |
| REQ-0032 | Canonical revisioning | Corrections, parser changes, provider revisions, and normalization changes must create identifiable canonical dataset revisions rather than silently rewriting accepted history. | PRD 13.2; D-017 | Data integrity | Market Data | M2 | Property, migration | Silent mutation | Active |
| REQ-0033 | Typed dataset metadata | Every M2 dataset revision must retain stable identity, schema, provider/request provenance, time range, configuration/build, upstream source references, integrity, quality, availability, retention, and licensing metadata. | PRD 11, 13.5; D-017 | Product behavior | Catalog/data | M2 | Schema, component | Lineage loss | Active |
| REQ-0034 | Explicit retrieval requirements | A caller must declare instrument, daily interval, bounded range, freshness, completeness, and provider constraints through a canonical versioned request identity. | PRD 14; D-018 | Product behavior | Market Data | M2 | Contract, property | Ambiguous retrieval | Active |
| REQ-0035 | Structured resolution status | Retrieval must expose dataset revision and distinguish fresh, stale, partial, invalid, corrupt, unavailable, refreshing, quota-blocked, and policy-blocked outcomes with safe remediation. | PRD 13.5, 14; D-018 | Product behavior | Market Data/operations | M2 | Contract, end-to-end | Hidden degradation | Active |
| REQ-0036 | Idempotent durable retrieval | Equivalent concurrent retrieval or repair requests must share durable idempotent work with stable progress, cancellation, retry, and restart behavior. | PRD 14, 29; D-018 | Quality attribute | Workflow/data | M2 | Component, concurrency, recovery | Duplicate work | Active |
| REQ-0037 | Gap detection and targeted repair | M2 must detect missing expected daily observations under its declared reference policy and repair only affected ranges while preserving unaffected accepted revisions and lineage. | PRD 10.2, 14; D-018 | Data integrity | Market Data | M2 | Property, integration | Partial/stale data | Active |
| REQ-0038 | Initial quality rules | Deterministic M2 validation must detect invalid OHLC relationships, negative volume, duplicate observations, identity/time inconsistencies, non-finite values, and declared range gaps and must produce visible quality findings. | PRD 9.3, 13, 15; PRD M2 | Data quality | Market Data/operations | M2 | Property, golden fixture | Poor data | Active |
| REQ-0039 | Safe storage inspection and cleanup | Users must be able to inspect usage/provenance and preview scoped cleanup; protected, pinned, catalog-required, or reproducibility-required material must not be silently deleted. | PRD 13.5, 14; D-014, D-015 | Product behavior | Cache/catalog | M2 | Component, security-negative | State loss/storage pressure | Active |
| REQ-0040 | M2 evidence-based completion | M2 is complete only when requirements, contracts, migrations, provider policy, fixtures, implementation, quality/security/failure tests, documentation, observability, risks, licensing, and residual limitations are traceably evidenced. | PRD 37–39; universal exit gate | Governance | Cross-cutting | M2 | Traceability audit | False completion | Active |


## M3 governed temporal correctness requirements

| ID | Title | Normative statement | Authority | Classification | Scope | Planned milestones | Verification class | Risk links | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| REQ-0041 | Approved interval set | OSCA must support exactly the approved market-data intervals `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d` for M3 interval-aware contracts. | PRD sections 8, 10-14; D-012-D-018 | Product behavior | Market Data | M3 | Test | M3-R-004 | Active | Unknown intervals fail closed. |
| REQ-0042 | UTC interval windows | Interval bars must use UTC start-inclusive/end-exclusive windows. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-002 | Active | Provider-local timestamps cannot redefine canonical windows. |
| REQ-0043 | Completed-bar cutoff | OSCA must classify an interval as complete only after its interval end plus declared publication lag has passed. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-002 | Active | Prevents current in-flight bars from becoming canonical. |
| REQ-0044 | Stock session evidence | Stock expected windows must be derived from accepted exchange-session evidence. | PRD sections 10-14; D-012-D-018 | Product behavior | Market Data | M3 | Test | M3-R-001 | Active | Replaces M2 weekday approximation. |
| REQ-0045 | Unresolved stock sessions | A stock interval without accepted session evidence must be unresolved and not repair eligible. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-001 | Active | Avoids false gap repair. |
| REQ-0046 | Crypto UTC boundaries | Crypto expected windows must be derived from UTC day boundaries. | PRD sections 10-14; D-012-D-018 | Product behavior | Market Data | M3 | Test | M3-R-003 | Active | Applies across all approved intervals. |
| REQ-0047 | Gap state taxonomy | Gap detection must distinguish observed, missing, unresolved, non-expected, and incomplete intervals. | PRD sections 10-14; D-004 | Product behavior | Market Data | M3 | Test | M3-R-001, M3-R-002 | Active | M2 date classifications remain compatible. |
| REQ-0048 | Repair eligibility | Repair automation must target only missing completed expected intervals. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-001, M3-R-002 | Active | Incomplete and unresolved intervals are excluded. |
| REQ-0049 | Resampling completeness | Resampling must derive a higher interval only from contiguous complete lower-interval bars that fully cover the target window. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-003 | Active | Partial coverage emits no derived bar. |
| REQ-0050 | Resampling OHLCV semantics | Resampling must aggregate open, high, low, close, and volume deterministically from source bars. | PRD sections 10-14; D-004 | Data integrity | Market Data | M3 | Test | M3-R-003 | Active | First open, max high, min low, last close, sum volume. |
| REQ-0051 | Resampling lineage | Every resampled bar must record lineage to every source bar used. | PRD sections 10-14; D-004, D-015 | Data lineage | Market Data | M3 | Test | M3-R-003 | Active | Supports reproducibility and inspection. |
| REQ-0052 | M2 compatibility | M3 must not change the accepted meaning of M2 daily-bar contracts. | PRD sections 37-39; D-004 | Compatibility | Market Data | M3 | Test, inspection | M3-R-004 | Active | Additive contracts are preferred. |

## M4 governed research project, analytics, and visualization requirements

| ID | Title | Normative statement | Authority | Classification | Scope | Planned milestones | Verification class | Risk links | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| REQ-0053 | Governed project identity | OSCA must represent each research project with stable identity, objective, horizon, lifecycle status, and immutable creation metadata. | PRD sections 18, 34, 38-39; D-023 | Product behavior | Research Projects | M4 | Test | M4-R-001 | Active | Projects are the durable container for research work. |
| REQ-0054 | Project timeline | Project timelines must record typed events for decisions, hypotheses, data revisions, analysis graphs, analytical outputs, visualizations, reports, and promotions. | PRD sections 18, 34; D-009, D-023 | Product behavior | Research Projects | M4 | Test | M4-R-001 | Active | Timeline events preserve research history. |
| REQ-0055 | Hypothesis records | Hypotheses must capture assumptions, expected outcomes, invalidation conditions, confidence, and lifecycle state. | PRD sections 19, 34; D-024 | Product behavior | Research Projects | M4 | Test | M4-R-001 | Active | Supports thesis evolution without erasing evidence. |
| REQ-0056 | Ad hoc promotion | Ad hoc exploration must be promotable into a governed project with selected dependencies, rationale, and captured context. | PRD sections 18, 34; D-023 | Product behavior | Research Projects | M4 | Test | M4-R-004 | Active | Promotion creates project evidence rather than anonymous global state. |
| REQ-0057 | Analysis graph contract | Analyses must be represented as typed dependency graphs with nodes, inputs, outputs, parameters, dependencies, quality policy, interval requirements, and producer identity. | PRD sections 15, 20; D-019, D-025 | Contract | Analytics | M4 | Test | M4-R-002 | Active | Internal in M4, packageable in M5. |
| REQ-0058 | Graph validation | Analysis graph validation must reject duplicate node identifiers, missing dependencies, dependency cycles, and unsupported provisional data use. | PRD sections 15, 20, 32; D-004, D-019 | Data integrity | Analytics | M4 | Test | M4-R-002 | Active | Execution planning fails closed. |
| REQ-0059 | Structured output taxonomy | Analytical outputs must distinguish observations, signals, findings, theses, recommendations, alerts, and reports. | PRD section 19; D-024 | Product behavior | Analytics | M4 | Test | M4-R-001 | Active | Composite scores are optional summaries. |
| REQ-0060 | Output provenance | Analytical outputs must retain project, graph, producer, dataset revision, parameter, effective-time, quality, and evidence provenance. | PRD sections 11, 19, 34; D-009, D-024 | Data lineage | Analytics | M4 | Test | M4-R-001 | Active | Outputs cannot be retained without dataset lineage when data-backed. |
| REQ-0061 | Visualization specification contract | Visualizations must be represented as declarative specifications that reference governed analytical output identities. | PRD section 21; D-026 | Contract | Visualization | M4 | Test | M4-R-003 | Active | No direct internal database access. |
| REQ-0062 | Visualization export metadata | Visualization exports must include reproduction metadata, producer identity, source outputs, format, generation time, and aggregation or downsampling disclosure. | PRD sections 21, 34; D-026 | Product behavior | Visualization | M4 | Test | M4-R-003 | Active | Exports remain reproducible. |
| REQ-0063 | Dashboard composition | Dashboard specifications must compose panels from governed visualization specifications without mutating underlying analyses. | PRD section 21; D-026 | Product behavior | Visualization | M4 | Test | M4-R-003 | Active | Initial dashboard contract only. |
| REQ-0064 | Report evidence | Evidence-backed reports must reference structured outputs, visualizations, assumptions, contradictions, and reproduction metadata. | PRD sections 17, 19, 34; D-022, D-024 | Documentation/product behavior | Reports | M4 | Test, inspection | M4-R-001 | Active | Report generation can be basic in M4. |
| REQ-0065 | Global catalog references | Project records must reference reusable global catalog resources without destructively mutating them. | PRD section 18; D-023 | Architecture constraint | Catalog/Research Projects | M4 | Test | M4-R-001 | Active | Global catalog implementation remains incremental. |
| REQ-0066 | Extension-compatible boundary | M4 built-in analyses and visualization contracts must remain compatible with later independent extension packaging. | PRD sections 15, 20; D-019, D-020 | Architecture constraint | Extensions/Analytics | M4, M5 | Inspection | M4-R-005 | Active | Packaging itself remains M5. |
| REQ-0067 | M3 compatibility | M4 must not weaken M3 interval, temporal, retrieval, lineage, retention, or provider-licensing semantics. | PRD sections 10-14, 37-39; D-004, D-040 | Compatibility | Cross-cutting | M4 | Test, inspection | M4-R-005 | Active | Provider promotion remains deferred. |
| REQ-0068 | M4 evidence-based completion | M4 is complete only when requirements, contracts, implementation, verification, documentation, traceability, risks, OpenSpec, and hosted Quality evidence are retained. | PRD sections 37-39; universal exit gate; D-046 | Governance | Cross-cutting | M4 | Traceability audit | M4-R-001-M4-R-005 | Active | Exit review required. |
