# OSCA Product Requirements Document

**Status:** Discovery draft  
**Product phase:** Product definition  
**Last updated:** 2026-07-17

## 1. Document purpose

This document defines the product requirements for OSCA before detailed architecture and implementation specifications are created. It is a living document: accepted decisions are normative, proposed material is provisional, and unresolved matters remain explicitly recorded.

OSCA will use specification-driven development, intent-driven development, and test-driven development. Product requirements established here will later be decomposed into traceable architecture decisions, specifications, milestones, acceptance criteria, and tests.

## 2. Working product definition

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies. It acquires and governs data from multiple sources, supports extensible analytics and AI models, produces explainable market and portfolio insights, and evaluates strategies through reproducible backtesting and realistic paper trading.

The initial product is a research and decision-support system with paper trading. It is not initially an autonomous live-trading system.

## 3. Product vision

Enable an individual investor or quantitative researcher to investigate markets, construct and compare analytical methods, evaluate machine-learning models and strategies, and understand the evidence behind recommendations without being locked into a particular data provider, model family, visualization technology, or deployment environment.

The platform should evolve safely from a personal research environment into a broader product without sacrificing reproducibility, data lineage, or modularity.

## 4. Product principles

1. **Evidence before recommendation.** Every conclusion should be traceable to data, transformations, models, parameters, and execution time.
2. **Determinism where correctness matters.** Price calculations, indicators, accounting, risk rules, backtesting, and cache invalidation must not depend on generative-model judgment.
3. **AI as a bounded capability.** Machine learning and language models produce predictions, rankings, interpretations, and recommendations with explicit confidence and provenance.
4. **Provider independence.** Data providers and model vendors are replaceable adapters behind stable contracts.
5. **Reproducibility by default.** Analyses and experiments must be repeatable using versioned inputs, configuration, code, and artifacts.
6. **Modularity with purpose.** Boundaries follow product capabilities and change patterns; distributable services are not required prematurely.
7. **Local ownership.** The initial platform should preserve user control of data, credentials, models, and costs.
8. **Transparent uncertainty.** Missing, stale, conflicting, revised, or low-quality information must be visible.
9. **Safe evolution.** New metrics, analyses, visualizations, providers, and models must be addable without destabilizing unrelated capabilities.
10. **No implied profitability.** The product evaluates evidence and uncertainty; it does not promise returns.

## 5. Accepted product scope

### 5.1 Included in the initial product boundary

- Stock and cryptocurrency market research
- Multi-source data acquisition
- Governed, inspectable, selectively cleanable cache
- Data validation, normalization, and provenance
- Extensible metrics, indicators, features, and analyses
- Machine-learning training, evaluation, comparison, and inference
- Language-model-assisted synthesis, explanation, reporting, and interaction
- Reproducible backtesting
- Forward evaluation through realistic paper trading
- Portfolio and risk analytics
- Interactive visualizations and generated reports
- Scheduled jobs, scans, and alerts
- Local workstation and optional personal-server deployment
- API, command-line, and web-application access where appropriate

### 5.2 Explicitly excluded from the initial product boundary

- Submission of live brokerage or exchange orders
- Autonomous control of real capital
- Multi-tenant SaaS operation
- Brokerage custody or movement of funds
- Social trading or public strategy marketplaces
- Guarantees of investment performance
- Cross-installation synchronization unless later approved

### 5.3 Future-compatible but not committed

- Broker and exchange execution adapters
- Hosted multi-user edition
- Collaboration and strategy sharing
- Native mobile clients
- Distributed service extraction
- Additional asset classes

## 6. Operating model

OSCA will use a local-first core with an optional personal-server deployment.

The initial implementation should be a single-user modular monolith with background workers. User interfaces and automation clients communicate through stable application interfaces. Internal modules remain independently testable and may be extracted into services only when supported by operational evidence.

The platform should support:

- Workstation deployment for private research and local models
- Personal-server deployment for remote access and scheduled operation
- Partial offline operation using valid cached data
- Replaceable persistence and compute adapters where justified
- Stable interfaces for a web UI, CLI, notebooks, and external automation

Initial milestones will not attempt multi-tenancy or synchronization between independent installations.

## 7. Target users and personas

### 7.1 Primary persona: technical individual investor/researcher

The primary user is technically capable, conducts personal market and portfolio research, and wants to combine configurable quantitative methods, ML, LLM assistance, backtesting, and paper trading. The user may work through the web application, CLI, API, or notebooks and expects inspectable evidence rather than opaque recommendations.

The primary experience must support sophisticated work without requiring the user to operate a distributed system or build every analytical capability from code.

### 7.2 Secondary persona: analytical investor

This user primarily consumes dashboards, reports, comparisons, alerts, and explanations. The user may configure analyses and paper portfolios but does not normally implement extensions.

The product should progressively disclose advanced controls and explain technical results without weakening their rigor.

### 7.3 Secondary persona: extension developer

This user adds or maintains data providers, metrics, analyses, feature transformations, models, strategies, and visualizations through documented extension contracts.

Extension development must have stable interfaces, validation, isolated testing, compatibility rules, and observable failure behavior.

### 7.4 Initial persona exclusions

OSCA is not initially optimized for:

- Completely passive users seeking unexplained buy or sell signals
- Institutional trading desks requiring team workflows and enterprise governance
- SaaS administrators managing tenants, billing, or organizational access
- Live-trading operators requiring production order execution

## 8. Initial market universe and instrument identity

### 8.1 Default market universe

The initial default universe includes:

- US-listed common stocks
- US-listed exchange-traded funds for benchmarks, sectors, and portfolio analysis
- Major spot cryptocurrencies and their supported trading pairs
- User-defined watchlists and research universes

Options, futures, perpetual contracts, leveraged tokens, foreign exchange, bonds, and non-US equities are not part of the initial default universe.

The domain model must not assume that all instruments are US-based or denominated in US dollars. Future markets and asset classes should be addable without redefining existing instrument identities.

### 8.2 Extending the supported universe

Users must be able to add instruments within an already supported asset class without changing application code, provided at least one configured data provider can supply the required capabilities.

Instrument addition should support:

- Discovery through provider search
- Registration from provider metadata
- Manual registration when discovery is unavailable
- One or more provider mappings per instrument
- Validation and duplicate detection
- Capability visibility, such as quotes, historical bars, fundamentals, news, or corporate actions
- Explicit unsupported or partially supported status
- Inclusion in watchlists and research universes

Adding a new symbol is distinct from adding a new asset class. A new asset class may require new domain behavior, validation, calendars, accounting rules, and provider adapters.

### 8.3 Canonical instrument identity

OSCA must maintain a provider-neutral instrument registry. A displayed ticker or provider symbol is not a stable primary identity.

A canonical identity must distinguish, as applicable:

- Asset class
- Underlying security or crypto asset
- Listing, exchange, or trading venue
- Base and quote assets for a crypto pair
- Trading, quote, and reporting currencies
- Effective dates and lifecycle status
- Stable external identifiers when available
- Provider-specific symbols and identifier mappings

The same ticker text may refer to different instruments, and the same instrument may have different symbols across providers. Symbol reuse, ticker changes, venue changes, delistings, and crypto pair differences must not overwrite historical identity.

### 8.4 Provider symbol mapping

Each data-source adapter resolves between its remote identifiers and OSCA canonical identities through explicit, time-aware mappings.

A mapping should contain:

- Canonical instrument identifier
- Provider identifier
- Provider symbol or pair notation
- Provider and dataset scope
- Venue or exchange context
- Validity interval when relevant
- Mapping provenance
- Verification state
- Supported data capabilities

Mappings must be inspectable and correctable. Provider data cannot enter normalized storage as an unverified ticker-only identity when ambiguity exists.

## 9. Intelligence model

OSCA uses both machine learning and language models, with explicit separation of responsibilities.

### 9.1 Machine learning

Machine learning may support:

- Forecasting and probabilistic estimation
- Classification
- Opportunity ranking
- Market-regime detection
- Anomaly detection
- Feature selection
- Pattern recognition
- Risk estimation
- Strategy parameter exploration
- Position-sizing recommendations for simulation

### 9.2 Language models

Language models may support:

- Natural-language exploration of platform data
- Research synthesis
- Explanation of quantitative results
- Report generation
- Extraction and classification of unstructured information
- Tool orchestration through approved capabilities
- Hypothesis generation
- Comparison of analyses and model results

Language-model output must not be used as a numerical source of truth. Claims should reference the data or artifacts used to produce them.

### 9.3 Deterministic responsibilities

Deterministic components remain authoritative for:

- Market-data normalization
- Indicator and metric calculation
- Portfolio accounting
- Fee, slippage, and tax assumptions
- Backtest execution
- Paper-order processing
- Risk limits
- Cache validity and invalidation
- Experiment identity and artifact resolution
- Data-quality rules

## 10. Time horizons and market-data granularity

### 10.1 Initial bar intervals

OSCA will support multi-timeframe OHLCV bar data from the beginning. The initial interval set is:

- One day (`1d`)
- One hour (`1h`)
- Fifteen minutes (`15m`)
- Five minutes (`5m`)
- One minute (`1m`) when available and justified

The time-series model must support additional validated intervals without embedding this initial set as a permanent closed enumeration. Weekly, monthly, and other intervals may be derived from sufficiently granular canonical data when the derivation is valid.

Tick, quote, and order-book data are outside the initial product boundary.

### 10.2 Temporal correctness

The platform must:

- Preserve source interval and timestamp semantics
- Distinguish completed bars from in-progress bars
- Represent exchange calendars, sessions, holidays, timezones, and daylight-saving transitions explicitly
- Support continuous 24/7 cryptocurrency markets
- Detect missing expected bars using the relevant market calendar and session policy
- Record resampling rules and upstream lineage
- Prevent silent substitution of an unavailable interval
- Allow strategies and analyses to declare interval, lookback, freshness, and session requirements
- Expose provider-specific interval availability and history limits

## 11. Artifact identity and lineage

Datasets, scans, features, models, predictions, reports, backtests, and paper-trading runs must have unambiguous identities.

A mutable pointer such as `latest` may exist only as a convenience. It must resolve to an immutable, typed artifact and cannot be the artifact's primary identity.

Every material artifact should expose, as applicable:

- Artifact type and schema version
- Stable unique identifier
- Creation and effective timestamps
- Producing workflow and version
- Source datasets and upstream artifacts
- Configuration and parameters
- Code or build version
- Model and prompt versions
- Market calendar and timezone assumptions
- Data-quality status
- Reproducibility status
- Retention and invalidation state

Artifact lookup must be type-aware so, for example, a training run cannot be mistaken for a scan merely because both belong to an intraday workflow.

## 12. Data-provider routing

### 12.1 Capability-based selection

OSCA will route data requests by capability rather than using one globally preferred provider. Independently configurable capabilities may include:

- Instrument reference data
- Historical bars by interval
- Current quotes
- Corporate actions
- Fundamentals and financial statements
- Analyst estimates
- News and sentiment inputs
- On-chain metrics
- Cryptocurrency market structure
- Macroeconomic and benchmark data

Each route has an ordered provider policy. Routing may consider instrument support, interval and history availability, freshness, measured quality, latency, monetary cost, quota state, licensing restrictions, and user preference.

### 12.2 Provider contracts

A provider adapter must declare machine-readable capabilities and limitations, including:

- Supported asset classes, venues, and instruments
- Data categories and intervals
- Available historical depth
- Expected freshness or delay
- Adjustment and timestamp semantics
- Authentication requirements
- Rate and quota constraints
- Licensing, persistence, and redistribution constraints
- Known quality limitations
- Health and availability state

Credentials must remain outside portable project configuration and exportable research artifacts.

### 12.3 Fallback and reconciliation

A request normally uses one selected source. Ordered fallback is allowed, but provider selection and fallback events become part of provenance.

A fallback cannot silently extend an existing logical series as if its values came from the primary provider. Provider transitions must remain visible as dataset segments or pass through an explicit, versioned reconciliation process.

Cross-provider comparison may detect gaps, conflicts, anomalies, or quality changes. It must not silently overwrite or average observations. Any merge, selection, or conflict-resolution method must be declared, deterministic, versioned, and reproducible.

Backtests and retained experiments must be able to pin provider, dataset identity, and revision.

## 13. Governed data layers and catalog

OSCA will separate cached data and research outputs into four logical layers. These layers define governance and lifecycle semantics and do not require four separate database technologies.

### 13.1 Source layer

The source layer contains immutable provider payloads or faithful snapshots when provider terms permit retention.

A retained source record includes its canonical request identity, provider, retrieval time, response metadata, checksum, parser compatibility, and applicable persistence restrictions. Source payloads are never silently modified.

License-restricted or sensitive content may be processed without permanent source retention. The catalog must record that the source payload was intentionally not retained.

### 13.2 Canonical layer

The canonical layer contains validated and normalized observations expressed through OSCA instrument identities, temporal semantics, units, currencies, and versioned schemas.

Corrections, improved parsing, provider revisions, and normalization changes create identifiable dataset revisions rather than silently rewriting data required by retained experiments.

### 13.3 Derived layer

The derived layer contains reproducible transformations, including:

- Resampled bars
- Indicators and metrics
- Features and labels
- Joined analytical datasets
- Data-quality assessments
- Screening and analysis outputs

Every derived result identifies its transformation definition and version, parameters, and upstream inputs.

### 13.4 Artifact layer

The artifact layer contains durable research and product outputs, including:

- Trained models
- Model evaluations and comparisons
- Prompt and LLM evaluation artifacts
- Backtests
- Paper-trading runs
- Reports and chart specifications
- Exported research packages

Artifacts reference their datasets and dependencies but are not treated as canonical market observations.

### 13.5 Cross-layer metadata catalog

A shared metadata and lineage catalog spans every layer and remains available even when a large payload is evicted.

The catalog tracks, as applicable:

- Stable identity and artifact type
- Schema and revision
- Provider and request provenance
- Upstream and downstream dependencies
- Quality findings
- Storage class and physical location
- Retention and pinning state
- Reproduction requirements
- Availability state
- Licensing restrictions
- Integrity checksums

Availability states must distinguish at least `available`, `evicted`, `expired`, `invalid`, `corrupt`, `partial`, and `reproducible`.

Promotion and transformation between layers must be explicit and observable. Cleanup uses dependency information and reports downstream impact before destructive execution.

## 14. Cache and data lifecycle — initial requirements

The cache is a first-class product capability rather than an incidental HTTP optimization.

It must eventually support:

- Provider-aware retrieval and rate-limit handling
- Canonical request identities
- Raw-response preservation where licensing permits
- Normalized and derived data layers
- Freshness policies based on data type and market state
- Gap detection and targeted repair
- Incremental retrieval
- Partial invalidation by provider, asset, interval, date range, dataset type, or derivation
- Total cleanup with explicit scope and impact preview
- Dependency-aware invalidation of derived artifacts
- Re-fetch after corruption, expiry, schema change, or manual invalidation
- Offline reads with visible freshness status
- Storage quotas, retention policies, and inspection
- Concurrency control and idempotent retrieval
- Provenance and audit events
- Protection against silently mixing incompatible revisions
- Configurable storage locations
- Global and category-specific storage budgets
- Retention policies based on data type, interval, age, recomputation cost, and user importance
- Storage-usage reporting by provider, asset, interval, layer, and artifact type
- Space forecasting and configurable warning thresholds
- Cleanup previews that show affected data and downstream artifacts
- Dry-run cleanup
- User-pinned data and artifacts protected from automatic eviction
- Safe automatic reclamation under explicit policies
- Detection and recovery from interrupted cleanup
- No silent deletion of inputs required by a retained reproducible experiment

Storage reclamation will use tiered, value-aware retention rather than pure time-to-live or least-recently-used eviction.

Storage classes include:

1. **Protected:** pinned datasets, promoted models, retained experiments, paper-trading records, manifests, and audit metadata.
2. **Canonical:** normalized market history that is costly or time-consuming to reconstruct.
3. **Source:** raw provider responses retained where licensing and policy permit.
4. **Derived:** indicators, features, resampled bars, temporary datasets, and intermediate artifacts.
5. **Ephemeral:** incomplete downloads, previews, scratch results, and failed-run intermediates.

Reclamation must consider class, age, interval, recomputation cost, provider availability, rate limits, lineage dependencies, and user pinning. It should normally evict reproducible derived data before expensive or irreproducible source data.

The system must retain lightweight identity, manifest, and lineage metadata when a large payload is evicted. Evicted artifacts must be visibly marked as unavailable or reproducible from identified sources. Automatic ingestion must pause safely when protected content alone exhausts the configured budget.

Storage-root relocation must copy or move data, verify integrity, and switch atomically enough to avoid silently losing the active store.

Storage management must make stable disk usage achievable without routine manual intervention. Defaults should be safe for a personal workstation, while users can adjust budgets and policies for larger personal-server deployments.

### 14.1 Retrieval triggers

Retrieval may be initiated on demand, by schedule, manually, as a workflow dependency, by detected gaps or invalidation, by provider revision or schema migration, or through a supported real-time feed.

### 14.2 Data requirement contracts

A request declares, as applicable:

- Instrument universe
- Data capability
- Interval and date range
- Required completion state
- Maximum acceptable staleness
- Provider or routing policy
- Adjustment policy
- Required quality level
- Whether partial results are allowed
- Whether stale data may be returned while refreshing
- Whether network access is allowed
- Whether the caller must wait for completion

Callers can select policies equivalent to `require_fresh`, `accept_stale`, `stale_while_revalidate`, and `offline_only`.

### 14.3 Resolution semantics

Cache resolution returns data references together with structured status. Status distinguishes at least fresh, stale, partial, unavailable, invalid, and refreshing.

Freshness evaluation considers data type, interval, market calendar, session state, provider behavior, and revision policy. Historical completed bars do not expire only because time passes, but may be revised or invalidated. In-progress bars are explicitly provisional.

Concurrent equivalent requests share one retrieval job. Retrieval is idempotent, supports resumable range backfills, and repairs missing ranges rather than downloading complete datasets unnecessarily.

Every analysis records the actual immutable dataset revision used, regardless of the freshness policy requested. Scheduled refresh prioritization should be configurable and may favor watched instruments and active paper portfolios.

Polling and streaming provider adapters must expose compatible normalized data-capability contracts.

Detailed cache and storage policy remains an open design area and will receive its own specification after product requirements are settled.

## 15. Extensible analysis and extension distribution

### 15.1 Capability taxonomy

OSCA distinguishes at least:

- Metrics
- Indicators
- Model features and labels
- Analyses and screeners
- Strategies
- Models
- Visualizations
- Data-provider adapters

Each category has a typed, versioned contract appropriate to its behavior.

### 15.2 Extension levels

OSCA supports:

1. **Declarative composition:** users assemble registered capabilities into versioned analysis definitions and dependency graphs without implementing new code.
2. **Code extensions:** developers implement genuinely new capabilities through governed extension interfaces.

Analyses should be represented as inspectable dependency graphs so reusable nodes can be cached, independent work can execute concurrently, and invalidation can target affected outputs.

### 15.3 Independent packaging and import

Code extensions do not need to reside in or be released with the OSCA application repository. Users and third parties can design, package, publish, import, update, disable, and uninstall extensions independently.

An extension package must provide a manifest containing, as applicable:

- Globally unique extension identity
- Name, publisher identity, and version
- Extension category and entry points
- OSCA compatibility range
- Input, output, and parameter schemas
- Supported asset classes and intervals
- Dependencies
- Required permissions and external access
- Determinism and random-seed behavior
- Lookback and warm-up requirements
- Missing and provisional data behavior
- Leakage-safety metadata for model features
- Resource requirements or limits
- Integrity information
- License and provenance

Import creates an installation record containing the exact package identity, version, source, integrity digest, resolved dependencies, granted permissions, and activation state. Retained analyses and artifacts continue to reference the exact extension versions that produced them.

Installing a newer version must not silently reinterpret a retained analysis. Compatibility is validated before activation. Disabling or uninstalling an extension must preview impacted definitions and retained reproducibility requirements.

### 15.4 Extension safety and conformance

Extensions must:

- Receive data through approved contracts
- Avoid direct mutation of canonical data
- Return typed results and structured diagnostics
- Attach provenance automatically
- Supply conformance tests or compatible fixtures
- Fail without corrupting unrelated workflows
- Respect declared resource and access constraints

Visualizations consume typed results rather than arbitrary internal tables. LLM tools invoke approved application capabilities rather than extension internals.

The exact extension runtime, package format, isolation mechanism, signing policy, and public registry design remain architectural decisions to be specified later.

## 16. Backtesting and paper trading — initial requirements

The platform must support fair, reproducible comparison of strategies and models.

It should eventually include:

- Point-in-time data handling
- Prevention and detection of look-ahead bias
- Survivorship-bias controls where relevant
- Configurable fees, spreads, slippage, latency, and liquidity assumptions
- Market calendars and cryptocurrency 24/7 trading
- Corporate-action handling
- Walk-forward and rolling-window evaluation
- Train, validation, test, and out-of-sample separation
- Baseline strategies
- Parameter-search tracking
- Portfolio-level constraints
- Deterministic seeds where applicable
- Comparable metrics across runs
- Backtest-to-paper-trading promotion
- Paper-order lifecycle and simulated fills
- Difference analysis between simulated expectations and forward results

## 17. Engineering-quality direction

The following process requirements are accepted in principle and will be specified before implementation:

- Product requirement to specification to test traceability
- Intent records explaining why material behavior exists
- Acceptance criteria defined before implementation
- Test-driven development for product behavior
- Unit, integration, contract, end-to-end, property, and performance tests according to risk
- Architecture decision records for consequential choices
- Versioned schemas and migration tests
- Reproducible development and test environments
- Automated quality gates
- Documentation treated as versioned product material
- No feature considered complete without observability and failure behavior appropriate to its risk

## 18. PRD sections pending discovery

The following areas are intentionally incomplete:

- User problems and primary workflows
- Product goals, non-goals, and measurable outcomes
- Detailed cache semantics
- Model and experiment lifecycle
- Backtest fidelity levels
- Portfolio and risk functionality
- Visualization and reporting experience
- Alerting and scheduled operation
- Security and credential handling
- Availability, performance, scalability, and cost objectives
- Import, export, backup, and recovery
- Milestone decomposition
- Product success metrics
- Risks and mitigations

## 19. Document governance

Accepted decisions are recorded in [decision-log.md](decision-log.md). A decision remains active until explicitly superseded. Open questions should not be silently converted into requirements.

Detailed architecture and technology selection are deferred until the relevant product requirements and quality attributes are accepted.
