# OSCA Glossary and Ubiquitous Language

- **Status:** Draft
- **Governing role:** Product authority
- **Approval roles:** Architecture authority and quality authority
- **Purpose:** Establish consistent meanings for product, domain, architecture, security, research, and engineering terms used across OSCA specifications and implementation.
- **Authoritative sources:** Product requirements; decisions D-001 through D-047; accepted ADRs
- **Downstream consumers:** Requirements catalog, domain model, module catalog, specifications, APIs, schemas, tests, documentation, and user interfaces
- **Review triggers:** Authoritative terminology changes, new module or public contract, milestone entry or exit, or detected inconsistent usage

## Usage rules

- Governed artifacts use the preferred term defined here when the distinction is material.
- A term cannot be redefined locally without an explicit scoped definition and compatibility analysis.
- Product-language terms describe user-visible concepts. Architecture terms must not leak into product language unless the architecture itself is relevant to the user.
- Provider, framework, database, and vendor terminology must not replace provider-neutral OSCA concepts.
- `ML` and `LLM` are used when their responsibilities differ. `AI` is an umbrella term only. `LM` is not used.
- A displayed ticker or provider symbol is never treated as a stable instrument identity.
- A mutable alias such as `latest` is never treated as an artifact identity.

## Product and operating model

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **OSCA** | The local-first market-intelligence and quantitative-research product defined by the approved PRD. | A trading bot, brokerage, exchange, or multi-tenant SaaS platform. |
| **Owner** | The single logical owner of an initial OSCA installation. The owner may use multiple clients and scoped automation credentials. | A SaaS tenant or unrestricted superuser assumed by every component. |
| **User** | A person interacting with OSCA. In initial scope this normally refers to the owner acting through a product interface. | An independently administered tenant member. |
| **Local-first** | An operating model in which the core product runs under the owner’s control, retains local ownership of data and credentials, and can provide useful cached operation without mandatory cloud services. | Local-only. OSCA may also run on a personal server and contact configured external providers. |
| **Workstation deployment** | OSCA running primarily for interactive private research on the owner’s computer. | A development environment, which is an engineering concern. |
| **Personal-server deployment** | A remotely accessible, authenticated OSCA installation operated for one logical owner, including scheduled and headless operation. | Multi-user hosted service or multi-tenant SaaS. |
| **Partial offline operation** | Use of valid governed cached data while network-dependent capabilities visibly degrade or remain unavailable. | Silent substitution, assumed freshness, or disconnected full functionality. |
| **Modular monolith** | One deployable product boundary whose internal capability modules have explicit ownership, contracts, dependency rules, and independent verification boundaries. | A layered shared-model monolith or a distributed microservice system. |
| **Background worker** | An execution mechanism that invokes governed application capabilities outside an interactive request while remaining inside the modular-monolith product boundary. | An independent business-logic tier or automatically separate service. |
| **Application capability** | A versioned operation exposed consistently to approved clients and governed by product validation, security, provenance, errors, and observability. | Direct database access or presentation-specific business logic. |

## Market identity and reference data

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Asset class** | A category whose members share material market, lifecycle, valuation, accounting, and data semantics, such as equity or spot cryptocurrency. | A watchlist category or provider product family. |
| **Asset** | The underlying economic security, fund, token, or currency-like object, independent of a particular listing or trading pair when that distinction applies. | Ticker text. |
| **Instrument** | A provider-neutral tradable or analyzable market object with a stable canonical identity and lifecycle. | Provider symbol, ticker, or database row ID used without domain meaning. |
| **Listing** | An instrument representation traded on a specific venue, normally for securities and funds. | The underlying asset or ticker text alone. |
| **Trading pair** | A spot cryptocurrency market defined by base asset, quote asset, and venue context where applicable. | A concatenated provider symbol assumed to be globally unique. |
| **Venue** | An exchange, market, or trading facility relevant to identity, sessions, calendars, or provider mappings. | Provider. A provider may source data for many venues. |
| **Canonical instrument identity** | OSCA’s stable, provider-neutral identity for an instrument, preserving lifecycle and historical continuity. | Provider symbol as primary identity. |
| **Provider mapping** | A time-aware association between a canonical instrument and a provider-specific identifier or symbol in a defined dataset and venue scope. | Permanent ticker equivalence. |
| **Instrument registry** | The governed collection of canonical instruments, lifecycle state, external identifiers, and provider mappings. | A flat symbol list. |
| **Universe** | A versioned or reproducibly defined collection of instruments used by a project, analysis, model, strategy, or policy. | A provider’s complete catalog unless explicitly selected. |
| **Watchlist** | A user-managed instrument collection for attention, navigation, retrieval priority, or monitoring. | A research universe whose exact membership must be reproducible unless promoted as one. |
| **Market calendar** | A versioned definition of sessions, holidays, timezones, and daylight-saving behavior for a venue or market. | A weekday-only assumption. |
| **Bar** | An interval market observation, normally OHLCV, with explicit timestamp, interval, completion state, source semantics, and revision. | Tick, quote, or order-book event. |
| **Completed bar** | A bar whose source interval has closed under the applicable market and provider semantics. | Immutable bar; providers may still issue revisions. |
| **Provisional bar** | An in-progress or otherwise not-final bar whose values may change. | Missing or invalid bar. |

## Providers, acquisition, data, and lineage

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Provider** | An external or local source that supplies a declared data or model capability through an adapter. | Venue, extension, or canonical authority. |
| **Provider capability** | A machine-readable statement of data category, instruments, intervals, history, freshness, authentication, quota, licensing, quality, and availability supported by a provider adapter. | A marketing feature name. |
| **Routing policy** | An ordered, capability-specific policy that selects a provider using explicit constraints and records fallback decisions. | One global default provider. |
| **Fallback** | Use of a lower-priority provider after the selected route cannot satisfy a request. The event is explicit provenance. | Silent cross-provider series continuation. |
| **Reconciliation** | A deterministic, versioned process that compares or resolves explicitly identified provider or dataset differences without silently overwriting observations. | Automatic averaging or hidden merge. |
| **Data requirement** | A caller’s structured declaration of instrument scope, capability, interval, range, completion, freshness, quality, adjustment, provider, partial-result, network, and waiting requirements. | An unqualified cache lookup. |
| **Retrieval job** | A durable, idempotent unit of acquisition or repair work that satisfies a data requirement and exposes status, progress, diagnostics, and provenance. | A raw HTTP request. |
| **Source layer** | Immutable provider payloads or faithful snapshots retained where policy permits. | Canonical market truth. |
| **Canonical layer** | Validated, normalized, revisioned observations expressed through OSCA identities, temporal semantics, units, and currencies. | In-place cleaned source rows. |
| **Derived layer** | Reproducible outputs produced from governed inputs by identified transformations, such as indicators, features, resampled bars, or analytical datasets. | Irreproducible notebook state. |
| **Artifact layer** | Durable research and product outputs such as models, evaluations, backtests, reports, chart specifications, and exported packages. | Canonical market observations. |
| **Dataset** | A typed, governed collection of observations or records with stable identity and declared semantics. | A mutable file path or table name used as identity. |
| **Dataset revision** | An immutable identifiable state of a dataset created by source revisions, parsing, normalization, repair, quality, or transformation changes. | Overwriting historical data in place. |
| **Artifact** | A typed, immutable or versioned durable output with stable identity, provenance, schema, producing workflow, configuration, and lifecycle metadata. | A mutable `latest` pointer. |
| **Provenance** | Information describing where data or an output came from, including provider, retrieval, transformation, model, prompt, code, configuration, and time context as applicable. | Lineage alone. |
| **Lineage** | Explicit upstream and downstream dependency relationships among datasets, transformations, artifacts, runs, and decisions. | A human-readable note with no stable references. |
| **Metadata catalog** | The shared governed index of identity, schema, revision, provenance, lineage, quality, storage, availability, retention, licensing, and integrity across data layers. | A physical database selection. |
| **Quality finding** | A versioned structured result from a data-quality rule, with severity, evidence, scope, impact, and remediation guidance. | Silent repair or generic warning text. |
| **Repair revision** | A new traceable dataset revision produced by an explicit deterministic correction or remediation transformation. | Mutation of prior canonical data. |
| **Availability state** | A structured state such as available, evicted, expired, invalid, corrupt, partial, or reproducible. | Boolean cache hit or miss. |
| **Freshness** | Whether data satisfies a declared policy considering data type, interval, market state, provider behavior, and revision policy. | Age alone. |
| **Retention policy** | A versioned rule governing preservation, eviction, cleanup, and protection based on storage class, dependencies, value, cost, age, provider recovery, and user pinning. | Pure TTL or LRU eviction. |
| **Pinned** | Explicitly protected from automatic reclamation by policy. | Guaranteed permanent regardless of corruption, migration, or explicit deletion. |

## Research organization and analytical results

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Global catalog** | Governed reusable installation-level resources such as instruments, provider policies, datasets, extensions, templates, promoted models, schedules, and system policies. | An unscoped dumping ground for research outputs. |
| **Research project** | The primary governed container for an objective-specific investigation, including intent, hypotheses, dependencies, analyses, models, results, reports, and reproducibility records. | Paper account or global catalog. |
| **Ad hoc workspace** | An identified temporary research context whose outputs are not yet promoted to a governed project. | Ambiguous global scratch state. |
| **Research intent** | A durable explanation of why an investigation or material behavior exists, including objective, constraints, assumptions, success criteria, and non-goals. | Implementation task description. |
| **Hypothesis** | A testable proposed explanation or expected relationship evaluated within a research project. | Thesis; a thesis is a structured analytical result with lifecycle and invalidation conditions. |
| **Analysis definition** | A versioned declarative graph or typed capability configuration that specifies inputs, dependencies, parameters, methodology, and outputs. | An execution result. |
| **Analysis run** | One identified execution of an analysis definition against exact inputs and versions. | The reusable definition. |
| **Metric** | A deterministic quantitative measurement with declared inputs, units, methodology, and applicability. | An interpretation or recommendation. |
| **Indicator** | A method-derived market or portfolio measure, often time-series based, used as evidence or an analysis input. | A guaranteed predictive signal. |
| **Feature** | A governed model input with explicit computation, timing, availability, lineage, and leakage constraints. | Arbitrary training column. |
| **Label** | A governed target or outcome definition with explicit horizon, timing, construction, and leakage constraints. | Future data used without point-in-time rules. |
| **Screener** | An analysis that filters or ranks a universe using declared criteria and produces typed results. | A provider symbol search. |
| **Observation** | A governed measured or retrieved fact with effective time, units, quality, freshness, and provenance. | An analyst opinion. |
| **Signal** | A method-specific interpretation of observations, identified by method, version, scope, interval, horizon, class or direction, strength, and dependencies. | Recommendation. |
| **Finding** | A structured analytical conclusion combining evidence and contradictions while preserving methodology, assumptions, quality, horizon, and provenance. | A single opaque score. |
| **Thesis** | A time-bounded testable analytical hypothesis with evidence, assumptions, expected outcomes, risks, invalidation conditions, and lifecycle state. | Research intent or recommendation. |
| **Recommendation** | An optional proposed simulated action produced by an explicit policy from findings or theses, portfolio state, and deterministic risk constraints. | Authoritative fact, live order, or guaranteed advice. |
| **Recommendation policy** | A versioned deterministic or governed rule set that converts eligible analytical results and state into a recommendation. | Strategy execution engine. |
| **Alert** | A notification-worthy occurrence tied to an analytical, data-quality, operational, security, thesis, recommendation, or risk condition. | Delivery channel; an alert may be delivered through several destinations. |
| **Evidence** | Governed observations, signals, findings, results, or identified external sources supporting or contradicting a conclusion. | Unreferenced narrative. |
| **Reproducibility manifest** | A durable record of exact datasets, revisions, definitions, versions, parameters, environment, and artifacts needed to reproduce or explain an output. | Backup package. |

## Visualization and reporting

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Visualization specification** | A typed, versioned, serializable declaration rendered by OSCA from governed results, including provenance and approximation metadata. | Executable arbitrary frontend code. |
| **Custom view** | A separately governed extension-provided interactive view with explicit trust, permissions, compatibility, and state-access constraints. | Standard visualization specification. |
| **Dashboard** | A saved composition of visualization panels and interactions that references governed results without mutating them. | Analysis definition or source of truth. |
| **Report** | A durable evidence-backed presentation artifact with identified inputs, methodology, version, and reproduction metadata. | A transient UI screenshot. |
| **Downsampling** | A disclosed deterministic reduction of displayed data volume that does not alter the full-resolution analytical input. | Silent analytical approximation. |

## Strategy evaluation and paper accounting

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Strategy** | A versioned definition that converts governed inputs into decisions or typed order intents under declared timing, data, and execution assumptions. | A recommendation narrative. |
| **Fidelity profile** | A named and versioned evaluation level with explicit semantics and limitations. | A generic `backtest` label. |
| **F0 signal study** | Evaluation of whether a signal predicts a defined outcome without simulating orders or a portfolio. | Portfolio backtest. |
| **F1 vectorized portfolio estimate** | Fast, explicitly non-authoritative portfolio approximation for compatible research questions. | Authoritative execution simulation. |
| **F2 event-driven bar simulation** | Authoritative initial-scope historical simulation using completed-bar events, order lifecycle, accounting, costs, liquidity, and deterministic risk. | Tick-level execution simulation. |
| **F3 forward paper evaluation** | Evaluation of an approved candidate using data as it becomes available and durable simulated portfolio behavior. | Historical backtest or live execution. |
| **Promotion** | An explicit governed decision allowing an eligible candidate to enter a later lifecycle stage, such as F2 validation or paper deployment. | Automatic selection of the best-looking result. |
| **Order intent** | A typed proposed simulated order before authoritative validation, deterministic risk evaluation, and acceptance. | Accepted order or live broker command. |
| **Paper order** | A simulated order accepted into the paper-account lifecycle. | Live brokerage or exchange order. |
| **Order event** | An immutable lifecycle event such as creation, acceptance, rejection, partial fill, fill, cancellation, or expiration. | Mutable order status as sole history. |
| **Fill** | A simulated execution event with quantity, price, time, costs, market evidence, and fill-model version. | Provider trade print assumed to be the account execution. |
| **Paper account** | A persistent simulated portfolio and accounting boundary independent of research-project ownership. | Research project or brokerage account. |
| **Journal entry** | An append-only balanced accounting record produced for a simulated economic event. | Mutable balance snapshot. |
| **Projection** | A rebuildable read model such as cash, position, lot, cost basis, exposure, or performance derived from authoritative events and journal entries. | Accounting authority. |
| **Reconciliation** | Verification that orders, fills, lifecycle events, journal entries, corporate actions, valuations, and projections are mutually consistent. | Provider reconciliation of market datasets unless explicitly qualified. |
| **Risk policy** | A versioned deterministic set of constraints evaluated at declared system, account, portfolio, strategy, and order-intent scopes. | Model or LLM judgment. |
| **Kill switch** | A system-wide control that pauses further paper automation without rewriting history. | Process termination as the primary safety mechanism. |

## ML and LLM lifecycle

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Experiment** | A governed ML investigation with exact data, features, labels, splits, code, environment, parameters, seeds, hardware context, and outputs. | One model file. |
| **Experiment family** | A related set of trials, including parameter searches, retained as a comparison context rather than only preserving a winner. | Model version. |
| **Model version** | An immutable identified trained model artifact plus required schema, configuration, evaluation, and provenance. | Mutable deployment alias. |
| **Model evaluation** | A task-specific governed assessment against baselines, uncertainty or calibration requirements, data partitions, robustness, and promotion criteria. | Training loss alone. |
| **Model deployment** | A controlled pointer from a declared use to one exact model version and policy context. | Copying over the previous model artifact. |
| **Champion** | The currently preferred model deployment candidate for a scoped paper use. | Permanent winner. |
| **Challenger** | A concurrently evaluated alternative model version under controlled comparison. | Unreviewed experiment. |
| **LLM gateway** | The governed provider-neutral capability that routes local or remote language-model operations under version, privacy, security, cost, tool, and evaluation policies. | Direct provider SDK calls from feature code. |
| **Prompt template** | A versioned governed instruction and input structure used in an LLM workflow. | Untracked runtime string. |
| **LLM tool** | A narrow typed application capability exposed to an LLM with explicit validation, permissions, provenance, and state-change policy. | Direct database or unrestricted shell access. |
| **Generated hypothesis** | An LLM-produced unsupported proposition clearly labeled for later evaluation rather than represented as a fact. | Finding with governed evidence. |
| **Untrusted content** | External or extension-provided text and data treated as input, never as privileged instructions. | System or developer instruction. |

## Extensions and capability packs

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Extension** | Independently packageable code implementing one or more governed public extension contracts. | Internal module or arbitrary plugin with privileged access. |
| **Capability pack** | A versioned collection of related analytical or provider capabilities with methodology, fixtures, tests, limitations, and usage documentation. | Unversioned script collection. |
| **Extension package** | An immutable distributable bundle plus manifest, integrity identity, dependencies, contracts, permissions, compatibility, license, and provenance. | Development directory itself. |
| **Installation record** | The exact package identity, source, digest, resolved dependencies, granted permissions, trust tier, and activation state recorded by an OSCA installation. | Package manifest alone. |
| **Installation** | Import and validation of an extension package into an inactive or eligible state. | Activation. Installation grants no implicit permissions. |
| **Activation** | Explicit enabling of an installed extension under approved compatibility and permissions. | Installation. |
| **Trust tier** | Built-in, verified, local-trusted, or untrusted/quarantined classification governing treatment and activation. | A guarantee that code is safe. |
| **Permission grant** | Explicit approval for a named extension capability such as network, credential, filesystem, subprocess, compute, or model access. | Unrestricted owner authority. |
| **Conformance suite** | Contract tests and fixtures proving an implementation satisfies required behavior, failure, provenance, compatibility, and isolation semantics. | Unit tests internal to the extension only. |

## Scheduling, operations, and recovery

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Workflow definition** | A versioned durable process definition with typed inputs, outputs, dependencies, idempotency, concurrency, checkpoints, and resource requirements. | One workflow run. |
| **Schedule** | A governed trigger and policy that initiates a workflow under explicit timezone, market-calendar, missed-run, resource, and notification semantics. | Operating-system cron entry as the sole source of truth. |
| **Job run** | One durable identified execution with state transitions, progress, lineage, resource use, diagnostics, and cancellation or recovery behavior. | Thread or process ID. |
| **Health finding** | A structured operational assessment describing state, impact, affected resources, evidence, and remediation. | Raw log line. |
| **Audit record** | A protected integrity-sensitive record of security, governance, permission, risk, or financially meaningful actions and outcomes. | Diagnostic log. |
| **Correlation identity** | A stable identifier connecting related requests, jobs, analyses, model operations, order intents, and journal events. | Artifact identity. |
| **Backup set** | An encrypted, integrity-manifested, compatibility-versioned recovery package created under a named backup profile. | Complete copy of every cache payload. |
| **Recovery point** | A mutually consistent logical state across required catalogs, journals, projects, deployments, locks, and dependencies. | Timestamp of file copying alone. |
| **Restore** | Validation and reconstruction of selected state into an isolated location before optional activation. | Immediate overwrite of active state. |
| **Recovery exercise** | A recorded isolated test proving integrity, restoration, reconciliation, smoke behavior, and recovery objectives without mutating the active environment. | Backup success notification. |
| **RPO** | Recovery-point objective: the maximum targeted amount of recent state loss measured in time. | Backup frequency alone. |
| **RTO** | Recovery-time objective: the targeted time to restore the declared capability or recovery class. | Full reconstruction of every evicted payload. |

## Engineering governance

| Preferred term | Definition | Avoid or distinguish from |
|---|---|---|
| **Product requirement** | An authoritative mandatory, recommended, optional, or conditional product obligation from the approved PRD or active product decision. | Implementation task. |
| **Catalog requirement** | An atomic testable requirement assigned an immutable `REQ-NNNN` identity and derived without semantic change from authoritative sources. | New product authority. |
| **Intent record** | A governed explanation of objective, value, constraints, assumptions, non-goals, and success evidence for a milestone or material behavior. | Specification of how to implement it. |
| **Specification** | A precise, testable definition of required behavior, contracts, invariants, acceptance criteria, failure semantics, and evidence for a bounded scope. | Aspirational design prose. |
| **Acceptance criterion** | An observable pass/fail condition defined before implementation and linked to requirements and verification. | General quality goal. |
| **ADR** | An architecture decision record selecting a consequential technical or engineering-governance approach within higher-level authority. | Product decision or informal design note. |
| **Architecture fitness check** | Automated or repeatable evidence that a structural architecture rule continues to hold. | One-time review only. |
| **Traceability** | Reviewable links connecting authority, intent, specification, acceptance, tests, documentation, ADRs, risks, and implementation evidence. | Identical text duplicated across files. |
| **Exit evidence** | The indexed objective evidence demonstrating a milestone satisfies every applicable exit criterion. | A completion assertion without references. |

## Terms intentionally not collapsed

The following distinctions are mandatory because collapsing them would weaken correctness or governance:

- asset, instrument, listing, trading pair, venue, ticker, and provider symbol;
- provider and venue;
- source, canonical, derived, and artifact layers;
- dataset identity and dataset revision;
- provenance and lineage;
- observation, signal, finding, thesis, recommendation, and alert;
- analysis definition and analysis run;
- strategy, recommendation policy, and risk policy;
- order intent, paper order, order event, and fill;
- journal authority and rebuildable projection;
- experiment, model version, evaluation, and deployment;
- extension installation and activation;
- dashboard, report, and visualization specification;
- workflow definition, schedule, and job run;
- backup set, recovery point, restore, and recovery exercise;
- local-first, local-only, personal-server, and multi-tenant operation.
