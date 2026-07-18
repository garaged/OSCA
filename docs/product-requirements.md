# OSCA Product Requirements Document

**Status:** Review candidate  
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

### 15.4 Extension trust and import sources

OSCA uses explicit extension trust tiers:

1. **Built-in:** released and tested with OSCA.
2. **Verified:** signed by an identified publisher and validated for compatibility and conformance.
3. **Local trusted:** imported from a local package or source repository and explicitly trusted by the user.
4. **Untrusted or quarantined:** inspectable and testable but inactive until the user approves its required permissions.

Supported or planned import sources include:

- Local extension bundles
- Local development directories
- Git repositories pinned to immutable commits or tags
- Direct package URLs with expected integrity digests
- A future OSCA extension registry

Installation and activation are separate actions. An extension receives no provider credentials or sensitive capabilities automatically. Manifests declare required network access, credential scopes, filesystem access, subprocess behavior, compute resources, and model execution.

Permission changes require renewed approval. Package digests and environment lockfiles support reproducibility. Analysis packages may declare required extensions but cannot silently install or activate them.

Publisher signatures establish identity and package integrity; they are not an unconditional guarantee of safety. A registry can improve discovery and verification but is not required for the initial extension system.

### 15.5 Extension safety and conformance

Extensions must:

- Receive data through approved contracts
- Avoid direct mutation of canonical data
- Return typed results and structured diagnostics
- Attach provenance automatically
- Supply conformance tests or compatible fixtures
- Fail without corrupting unrelated workflows
- Respect declared resource and access constraints

Visualizations consume typed results rather than arbitrary internal tables. LLM tools invoke approved application capabilities rather than extension internals.

The exact extension runtime, package format, isolation mechanism, signing implementation, and public registry design remain architectural decisions to be specified later.

## 16. Product interfaces

### 16.1 Web-primary experience

The web application is OSCA's primary interactive product experience. It covers market discovery, dashboards, analysis composition, experiment comparison, cache and storage management, paper trading, reports, alerts, and extension administration.

### 16.2 Versioned application API

Web, CLI, notebook, LLM, and future clients use shared, versioned application capabilities. Business rules must not be independently implemented in presentation clients.

Long-running operations return durable job identities and progress state. Local mode may optimize transport, but observable behavior remains compatible with personal-server operation.

### 16.3 Command-line interface

The CLI is mandatory for automation, scheduled workflows, bulk operations, diagnostics, backup and recovery, cache administration, extension development, and headless personal-server management. It need not reproduce interactions that are intrinsically visual.

### 16.4 Notebook integration

Notebooks access governed datasets through supported query interfaces and publish durable results through artifact interfaces. Direct database access is not a supported normal workflow.

### 16.5 Language-model interface

LLMs interact through approved application tools with the same validation, provenance, and structured error behavior as other clients.

### 16.6 Cross-interface requirements

All interfaces receive consistent validation, security enforcement, provenance, and errors. Visualizations can export underlying data and reproduction metadata. API compatibility is explicitly versioned.

## 17. Usage and operational documentation

Documentation is a required product capability and a release-blocking part of the definition of done.

Version-matched documentation must include, as applicable:

- Installation and upgrades
- Local and personal-server deployment
- Initial configuration and onboarding
- Instrument discovery and registration
- Provider configuration, capabilities, credentials, quotas, and limitations
- Data freshness, quality, provenance, and revision interpretation
- Cache inspection, storage budgets, cleanup, relocation, and recovery
- Analysis composition and execution
- Metric and indicator interpretation
- ML and LLM capability limitations
- Backtesting methodology and bias controls
- Paper-trading assumptions and workflows
- Portfolio and risk metric interpretation
- Visualization, reporting, export, and reproducibility
- Scheduled jobs and alerts
- CLI reference and task-oriented examples
- API reference, schemas, compatibility, and examples
- Notebook integration
- Extension development, packaging, testing, publishing, permissions, installation, and troubleshooting
- Backup, restore, diagnostics, and disaster recovery
- Security and credential-management guidance
- Known limitations and troubleshooting
- A domain glossary

User-facing behavior is incomplete until its task-oriented usage documentation is available. Examples and commands should be executable or automatically validated where practical. Documentation must identify the product version it describes and be updated in the same change as affected behavior.

Generated reference material may supplement but cannot replace conceptual guidance, tutorials, operational runbooks, and realistic end-to-end examples. Contextual help in the web application should link to the relevant versioned documentation.

## 18. Research organization

### 18.1 Global catalog

The global catalog contains reusable and system-level resources, including:

- Canonical instruments and provider mappings
- Provider capabilities and routing policies
- Governed dataset identities
- Installed extensions
- Reusable analysis templates
- Promoted models
- Credentials and security policies
- Schedules and system defaults

Global resources cannot be destructively changed without identifying affected projects, analyses, artifacts, and paper accounts.

### 18.2 Research projects

A research project is the primary container for an objective-specific investigation. It may contain:

- Research objective, intent, decisions, hypotheses, and notes
- Instrument universe
- Provider, freshness, interval, and date-range policies
- Analysis definitions and dependency graphs
- Features and labels
- Model experiments and comparisons
- Backtests
- Findings
- Dashboards and reports
- Extension and environment lockfiles
- Reproducibility manifests

Projects reference immutable datasets and artifacts rather than duplicating all underlying data. Project defaults can override system defaults without mutating them. Reusable content is promoted deliberately into the global catalog.

Projects can be cloned, archived, compared, exported, and imported. Exports may be thin manifests or self-contained packages, subject to data-provider licensing.

Every durable analysis, backtest, and report belongs to an explicit project. Short-lived work belongs to an identified ad hoc workspace rather than an ambiguous global context.

### 18.3 Paper accounts

Paper accounts are persistent simulated portfolios independent of research projects. They may consume promoted strategies, model versions, or recommendations from one or more projects without transferring ownership of portfolio history to those projects.

### 18.4 Language-model context

LLM operations receive the explicitly selected project context and approved global references. The system must not silently mix unrelated project histories into an explanation or recommendation.

## 19. Analytical output model

OSCA uses connected but distinct analytical result types.

### 19.1 Observation

A measured or retrieved fact from governed data, including its effective time, units, quality, freshness, and provenance.

### 19.2 Signal

A method-specific interpretation of one or more observations. A signal identifies the method and version, scope, interval, horizon, direction or class, strength, and dependencies.

### 19.3 Finding

A structured analytical conclusion combining one or more signals. A finding preserves supporting and contradicting evidence rather than reducing all evidence to an opaque score.

### 19.4 Thesis

A time-bounded, testable hypothesis containing assumptions, evidence, expected outcomes, risks, and invalidation conditions. Thesis states include active, weakened, invalidated, expired, and confirmed.

### 19.5 Recommendation

An optional proposed simulated action produced by an explicit recommendation policy. It consumes findings or theses, portfolio state, and deterministic risk constraints. A recommendation is not an authoritative fact and does not directly place a live order.

### 19.6 Alert

A notification that an observation threshold, signal, finding, thesis change, recommendation condition, data-quality event, operational condition, or risk event occurred.

### 19.7 Common analytical metadata

Results include, as applicable:

- Instrument, universe, or portfolio scope
- Producing analysis identity and version
- Effective time, expiration, and investment horizon
- Direction or classification
- Strength or materiality
- Confidence and calibration method
- Supporting and contradicting evidence
- Assumptions
- Data quality and freshness
- Applicable market regime
- Expected outcome distribution
- Invalidation conditions
- Relevant risks
- Provenance and dependencies
- Lifecycle state
- Evaluation outcome once sufficient future data exists

Composite scores are optional summary fields rather than complete analytical outputs. Their construction must be versioned and explainable.

LLMs may generate narrative explanations, but referenced evidence and deterministically calculated values remain authoritative.

## 20. Analysis families and capability packs

OSCA treats the following as first-class analysis families:

- **Market and technical:** price, volume, trends, momentum, volatility, support and resistance, patterns, and market structure
- **Fundamental and valuation:** financial statements, growth, profitability, quality, leverage, cash flow, valuation multiples, estimates, and revisions
- **Quantitative and statistical:** returns, distributions, correlations, factor exposures, seasonality, anomalies, regime detection, and statistical tests
- **Portfolio and risk:** allocation, exposure, drawdown, concentration, diversification, liquidity, stress testing, and scenarios
- **Macroeconomic and cross-market:** rates, inflation, currencies, commodities, indices, liquidity conditions, and intermarket relationships
- **Events and catalysts:** earnings, dividends, splits, listings, regulatory events, economic releases, and project-specific events
- **News and sentiment:** classification, entity extraction, source comparison, narrative shifts, and sentiment
- **Crypto-specific:** on-chain metrics, token supply, network activity, exchange flows, liquidity, funding, open interest, liquidation conditions, and tokenomics
- **Machine learning:** forecasting, classification, ranking, anomaly detection, feature importance, and calibrated uncertainty
- **LLM synthesis:** evidence summaries, comparisons, explanations, research assistance, and hypothesis generation
- **Strategy and outcome:** signal effectiveness, execution assumptions, trade distributions, robustness, and regime-specific performance

Implementations are delivered through versioned built-in or independently distributed capability packs. Equivalent methods may coexist and be compared.

Every analysis declares required provider capabilities, supported instruments and intervals, methodology, assumptions, degradation behavior, and structured outputs. Missing optional or premium data disables only dependent capabilities.

Capability packs include appropriate fixtures, tests, references, methodology documentation, limitations, and usage guidance. They access data through governed contracts rather than privileged internal storage.

### 20.1 Initial built-in analytical foundation

The first usable foundation includes:

- Data-quality analysis
- Returns and benchmark comparisons
- Core technical indicators
- Volatility and drawdown
- Correlation and diversification
- Portfolio exposure and risk
- Screening and ranking
- Backtest performance metrics
- Structured findings and reports

Deeper fundamental, macroeconomic, news and sentiment, crypto and on-chain, and specialized ML functionality can arrive as subsequent built-in or independent packs without changing the analytical output model.

## 21. Visualization and dashboards

### 21.1 Declarative visualization specifications

Analyses normally return typed, versioned, serializable visualization specifications rendered by OSCA. Specifications reference governed analytical results rather than arbitrary internal database queries.

The standard visualization grammar supports, as it evolves:

- Price and candlestick charts
- Indicators and overlays
- Volume and market-profile views
- Line, area, bar, and stacked charts
- Scatter and bubble plots
- Distributions and box plots
- Correlation and return heatmaps
- Drawdown and underwater charts
- Equity curves
- Rolling risk and performance charts
- Portfolio allocation and exposure
- Factor exposure and feature importance
- Prediction, confusion, and calibration diagnostics
- Event and catalyst timelines
- Backtest trades and annotations
- Tables with conditional formatting
- Structured evidence and thesis panels

### 21.2 Interactive dashboards

Users can assemble reusable dashboard panels and save interactive views without mutating underlying analyses.

Dashboards support, where meaningful:

- Filters and scoped parameters
- Linked selections and cross-filtering
- Drill-down
- Comparable instruments, portfolios, analyses, or experiments
- Synchronized time ranges
- Inspection of provenance, effective time, units, freshness, and quality

Large datasets use disclosed aggregation or downsampling. Users must be able to distinguish displayed approximations from full-resolution analytical inputs.

### 21.3 Export, reporting, and accessibility

Visualizations export images, tabular data, and reproduction metadata. The system supports static report rendering without the interactive client.

Visualizations provide keyboard operation, screen-reader descriptions, non-color encodings, and accessible summary tables as appropriate.

### 21.4 Governed custom views

Specialized extensions may provide custom frontend views only through a separately governed, permissioned, and compatibility-versioned interface. Custom views cannot access unrelated application state or bypass data contracts.

LLM-generated chart requests compile into validated visualization specifications rather than executable frontend code.

## 22. Backtesting and paper trading — initial requirements

The platform must support fair, reproducible comparison of strategies and models through named fidelity profiles and a dual-stage execution model.

### 22.1 Fidelity profiles

#### F0 — Signal study

Evaluates whether a signal predicts a defined future outcome without simulating orders or a portfolio. It enforces information availability, identifies the prediction horizon, compares baselines, and evaluates statistical significance and stability.

#### F1 — Vectorized portfolio estimate

Approximates positions, returns, rebalancing, exposure, fees, slippage, and risk through vectorized computation. F1 is fast and explicitly non-authoritative.

#### F2 — Event-driven bar simulation

Provides authoritative historical validation for initial OSCA scope using completed-bar events, typed order intents, order lifecycle, calendars, deterministic risk, accounting, costs, latency, liquidity constraints, partial fills, corporate actions, and multi-asset or multi-currency behavior.

F2 is bar-based and cannot claim tick-level execution accuracy.

#### F3 — Forward paper evaluation

Evaluates an approved candidate using data as it becomes available, including actual provider latency, outages, provisional and revised data, durable paper accounting, operational failures, missed schedules, drift, and realized outcomes.

F3 is forward evaluation rather than a historical backtest.

A possible future F4 microstructure profile using tick, quote, or order-book data remains outside initial scope.

Every result names its fidelity profile and versioned assumption set. Comparisons require compatible profiles and assumptions or disclose semantic differences. Asset- and market-specific defaults support optimistic, base, and stressed scenarios plus sensitivity analysis.

Unsupported behavior is reported rather than approximated silently. Higher fidelity does not compensate for leaked or invalid data. Promotion to paper trading requires F2 validation.

### 22.2 Dual-stage execution model

The platform must support fair, reproducible comparison of strategies and models through a dual-stage execution model.

### 22.3 Research/vectorized mode

Research mode provides fast evaluation for compatible factor studies, signal evaluation, screening, and broad parameter exploration. Its outputs are labeled research estimates rather than authoritative execution simulations.

### 22.4 Event-driven simulation mode

Event-driven mode is the authoritative strategy simulation. It uses the same event, order, fill, fee, portfolio, and deterministic risk concepts as paper trading.

The event-driven engine models, as applicable:

- Clocks, sessions, and market events
- Strategy decisions and typed order intents
- Order validation and lifecycle states
- Rejected, cancelled, partially filled, and filled orders
- Fees, spreads, slippage, latency, and liquidity constraints
- Corporate actions
- Cash, positions, exposure, and deterministic risk rules

Strategies declare supported execution modes. Compatible implementations use cross-engine conformance fixtures, and result differences between research and event-driven modes are visible and explainable.

Candidates are promoted from research mode to event-driven validation before paper trading. Promotion policies may require minimum sample sizes, robustness, risk limits, walk-forward or out-of-sample performance, and comparison against baselines.

The platform must support fair, reproducible comparison of strategies and models.

It should eventually include:

- Point-in-time data handling
- Prevention and detection of look-ahead bias
- Survivorship-bias controls where relevant
- Market calendars and cryptocurrency 24/7 trading
- Walk-forward and rolling-window evaluation
- Train, validation, test, and out-of-sample separation
- Baseline strategies
- Parameter-search tracking with nested, walk-forward, or otherwise leakage-resistant selection
- Portfolio-level constraints
- Deterministic seeds where applicable
- Comparable metrics across runs
- Explicit research-to-event-validation-to-paper-trading promotion
- Paper-order lifecycle and simulated fills
- Difference analysis between simulated expectations and forward results

## 23. Paper-accounting model

### 23.1 Order-event history

Paper accounts retain immutable order lifecycle events, including creation, acceptance, rejection, partial fill, fill, cancellation, expiration, and applicable validation or risk decisions.

Orders link to their originating strategy decision, recommendation, project, model, and evidence where available. Fills link to the market observation and fill-model version used.

### 23.2 Immutable accounting journal

Every simulated economic event creates balanced, append-only journal entries. Corrections use reversals and replacement entries rather than rewriting prior history.

Journaled events include, as applicable:

- Simulated funding deposits and withdrawals
- Trade fills
- Fees and other costs
- Dividends and distributions
- Splits, mergers, symbol changes, and delistings
- Interest
- Foreign-exchange effects
- Manual adjustments

Crypto-specific events such as staking rewards and network distributions can be added through typed event extensions.

### 23.3 Multi-currency valuation

Each paper account has an explicit base currency while holding cash and instruments in other currencies. Valuations record the price sources, foreign-exchange rates, effective times, and revisions used.

### 23.4 Rebuildable projections and reconciliation

Cash balances, positions, lots, cost basis, realized and unrealized profit or loss, exposure, equity curves, performance, and risk metrics are rebuildable projections rather than independent sources of truth.

Performance snapshots may accelerate reads but must be regenerable. Reconciliation verifies balanced journal entries and consistency between orders, fills, corporate actions, journal records, and projections.

Paper-account history does not change because a strategy, extension, or model is upgraded. Tax reporting is not initially authoritative, although lot and cost-basis information is retained for future analysis.

## 24. Machine-learning lifecycle

### 24.1 Governed experiments and model registry

OSCA supports pluggable training workflows while standardizing experiment identity, lifecycle records, evaluation contracts, and deployment control.

A model version is immutable. A deployment references an exact model version and can change without rewriting historical decisions or results.

Lifecycle states include:

1. Draft experiment
2. Training candidate
3. Evaluated candidate
4. Event-driven validated
5. Approved for paper deployment
6. Active paper champion or challenger
7. Suspended
8. Retired

### 24.2 Reproducible training records

Training records include, as applicable:

- Dataset and revision identities
- Feature and label definitions
- Sampling and weighting
- Temporal availability rules
- Training, validation, test, walk-forward, and forward-period definitions
- Code and extension versions
- Dependencies and environment
- Parameters and random seeds
- Material hardware context
- Produced model artifacts and integrity information

Feature contracts explicitly define timing and information availability to prevent leakage.

### 24.3 Evaluation and promotion

Evaluation is task-specific and includes uncertainty or calibration where meaningful. Simple baselines and non-ML strategies are mandatory comparison candidates.

Hyperparameter searches are retained as experiment families rather than preserving only the winning run. Final held-out data cannot be reused repeatedly for model selection.

Promotion policies may enforce data quality, minimum sample size, stability, risk, robustness, explainability, and event-driven validation.

### 24.4 Paper deployment and monitoring

Champion and challenger deployments support controlled forward comparison. Monitoring covers:

- Input and feature distributions
- Feature availability
- Prediction distributions
- Calibration
- Realized outcomes
- Operational errors and latency
- Applicable market-regime changes

Retraining may be scheduled or triggered but never implies automatic promotion. Rollback changes the deployment pointer to a prior immutable model version.

Model import and export use manifests and security validation. Unsafe or unsupported serialization formats can be rejected or quarantined.

Reinforcement-learning models follow the same governance and remain bounded by deterministic portfolio and risk rules.

## 25. Language-model lifecycle and gateway

### 25.1 Provider-neutral gateway

OSCA uses a governed provider-neutral gateway for local and remote LLMs. Routing may consider task capability, privacy, user preference, context limits, latency, availability, and cost.

Provider or model upgrades cannot silently replace the exact version used by a retained workflow.

### 25.2 Bounded application tools

LLMs access narrow, typed application capabilities rather than internal databases. Tool permissions follow user, project, extension, and data-source policy.

Read operations and state-changing operations are distinct. State-changing operations are disabled by default for imported workflows and require explicit policy or confirmation. No LLM tool can place a live order.

Paper-trading actions initiated through an LLM retain the initiating request, model and prompt identities, tool calls, applicable policy, recommendation, and resulting state changes.

### 25.3 Versioned and validated interactions

OSCA versions:

- Prompt templates and system instructions
- Tool definitions and schemas
- Retrieval and context-selection policies
- Model and provider configuration
- Structured output schemas
- Workflow definitions

Structured output is schema-validated before use. Generated claims reference governed observations or identified external sources. Unsupported claims are labeled as generated hypotheses.

### 25.4 Privacy, untrusted content, and resource budgets

Sensitive-data disclosure is controllable and previewable by provider and task. Local models may be preferred for private workloads.

External news, filings, web content, provider text, and extension output are treated as untrusted data rather than privileged instructions.

LLM operations support configurable token, monetary, latency, and tool-call budgets. Response caching considers model version, prompt version, context digest, permissions, provider policy, and privacy classification.

### 25.5 LLM evaluation

Evaluation covers, as applicable:

- Factual grounding
- Evidence and citation correctness
- Numerical consistency
- Structured-output validity
- Refusal and boundary behavior
- Prompt-injection resistance
- Tool selection and argument correctness
- Task completion
- Cost and latency
- Stability across supported model changes

## 26. Security, identity, and transport

### 26.1 Deployment-aware authentication

OSCA has one logical owner initially while retaining internal capability and scope enforcement.

Local-only mode binds to loopback or a protected local channel by default and relies on the operating-system user boundary. Binding to another network interface requires explicit configuration.

Personal-server access requires authenticated sessions and secure transport. Unsafe public exposure should be detected and rejected where practical.

Automation credentials are scoped, individually revocable, and expiring where practical. Extensions and LLM tools receive explicitly approved capabilities rather than unrestricted owner authority.

### 26.2 Secrets

Provider, LLM, and other credentials use an operating-system credential store or replaceable encrypted secret-vault adapter.

Secrets must not appear in logs, exception messages, URLs, manifests, project exports, ordinary backups, or diagnostic bundles. Backup and restore preserve secret references separately and require secure credential reconfiguration where needed.

Extensions receive approved named credential capabilities and cannot read the secret vault directly.

### 26.3 Network transport and endpoint authentication

All non-local network transfers use encrypted and authenticated transport appropriate to the protocol. Plaintext fallback is prohibited.

Requirements include:

- Modern TLS with secure defaults and obsolete protocols and ciphers disabled
- Server identity and hostname validation
- Trusted certificate-chain validation
- Fail-closed behavior for invalid, expired, mismatched, or untrusted certificates
- No routine configuration switch that disables certificate verification
- Client authentication on every protected remote application operation
- Mutual TLS for controlled machine-to-machine channels where OSCA controls or configures both endpoints and the operational profile requires it
- Provider-supported client authentication, such as OAuth, signed requests, scoped tokens, or API credentials, for external services that do not support client certificates
- Credential rotation and revocation
- Replay resistance where applicable
- No secrets in query strings
- Audit events for authentication and security-sensitive failures

Remote browser access uses TLS for server authentication plus authenticated application sessions. Remote automation can combine mutually authenticated transport with scoped application credentials so transport identity and application authorization remain distinct.

Certificate and trust-store configuration must be inspectable, testable, and documented. Certificate renewal and failure behavior require operational runbooks and automated health warnings.

Security profiles should map requirements to applicable deployment context and documented regulatory or organizational controls rather than claiming one universal regulation mandates the same authentication mechanism for every connection.

### 26.4 Application security

Session handling includes request-forgery protection, secure cookie policy, expiration, explicit logout, and appropriate rate limiting. Security-sensitive actions generate audit events.

Threat modeling, dependency and secret scanning, security tests, and secure configuration documentation are release requirements.

A future multi-user edition must replace rather than stretch single-owner identity assumptions.

## 27. Backup, restore, and disaster recovery

### 27.1 Policy-aware backup profiles

OSCA provides:

- **Lightweight backup:** required user state, configuration, identity mappings, journals, manifests, locks, schedules, and audit metadata
- **Standard backup:** lightweight content plus protected artifacts and selected datasets
- **Archival backup:** the maximum self-contained reproducible set permitted by storage, security, and provider licensing

Ephemeral data, in-progress downloads, transient caches, and secrets are excluded. Packages report all exclusions and identify content that must be re-fetched or reconfigured.

Backups are encrypted using user-controlled recovery material, contain integrity manifests and compatibility versions, and support scheduled retention policies and failure alerts.

### 27.2 Consistent recovery points

Backup creation produces a consistent logical recovery point. Running jobs either continue through supported snapshot semantics or pause at documented safe boundaries.

Paper-account journal boundaries, project references, catalog revisions, model deployments, extension locks, and artifact dependencies must remain mutually consistent.

### 27.3 Restore

Restore supports:

- Preview and compatibility assessment
- Integrity and authenticity verification
- Selective recovery by project, paper account, model, or artifact
- Restore to a new location before optional activation
- Explicit conflict policies
- Versioned schema migration
- Journal reconciliation
- Catalog and dependency validation
- Artifact checksum verification
- Reporting of unavailable or reproducible-from-source payloads

Restored state does not become active until required validation succeeds or the user explicitly accepts documented degraded recovery.

### 27.4 Disaster-recovery program

OSCA maintains a disaster-recovery program appropriate to workstation and personal-server deployment. It covers at least:

- Storage-device loss
- Database or catalog corruption
- Accidental deletion or invalid cleanup
- Failed application or schema upgrade
- Compromised or lost server
- Lost certificate or credential material
- Extension-caused corruption
- Interrupted backup, restore, or storage relocation
- Provider data becoming unavailable
- Loss of a protected model or experiment artifact

The program defines recovery-point objectives, recovery-time objectives, restoration priority, dependencies, roles, escalation, validation, and acceptable degraded operation.

Recovery priority is:

1. Security and identity configuration
2. Catalog, canonical identities, and system configuration
3. Paper-account journal and audit history
4. Research projects, intent, and reproducibility manifests
5. Extension locks, model registry, and protected artifacts
6. Reconstructable canonical and derived data
7. Ephemeral content

At least one backup copy can be stored off-device through authenticated encrypted transport. Archival policy should support separation from the active storage failure domain.

Operational documentation includes scenario-specific runbooks, recovery-material handling, certificate renewal and replacement, clean-system restoration, and post-recovery verification.

### 27.5 Recovery verification

Backup success alone is insufficient. OSCA supports:

- Automated package integrity checks
- Periodic restore tests into isolated storage
- Scheduled disaster-recovery exercises
- Reconciliation and smoke tests after restoration
- Recorded exercise results, duration, failures, and remediation
- Alerts for missed backups, failed verification, expired recovery material, or objectives at risk

Recovery tests must not mutate the active environment.

### 27.6 Default recovery objectives

OSCA uses tiered recovery classes:

| Recovery class | Examples | Default RPO | Default RTO |
|---|---|---:|---:|
| Critical state | Paper journals, canonical identities, configuration, project manifests, schedules | 1 hour | 4 hours |
| Active research | Project definitions, notes, findings, and experiment metadata | 4 hours | 8 hours |
| Protected artifacts | Promoted models, pinned datasets, reports, and extension locks | 24 hours | 24 hours |
| Reconstructable data | Downloadable canonical data and reproducible derivations | No payload guarantee | Catalog within 4 hours; payloads restored on demand |
| Ephemeral data | Temporary downloads and intermediates | None | None |

An optional hardened profile targets a 15-minute RPO and one-hour RTO for critical state when continuously reachable off-device storage is configured.

Objectives apply while OSCA and its configured destination are operational. The platform reports objectives currently at risk. Recovery can restore a safe degraded mode before all reconstructable data is available, but paper automation remains paused until journal reconciliation, required data, credentials, and risk controls are healthy.

Default verification includes monthly isolated restore tests and at least quarterly disaster-recovery exercises. Retention supports configurable hourly, daily, weekly, and monthly recovery points. Relaxed, standard, and hardened profiles make their protection and risks visible.

## 28. Observability and operational health

### 28.1 Built-in health center

OSCA provides an integrated health experience covering:

- Application, catalog, and persistence health
- Background jobs, queues, retries, and failures
- Provider availability, quotas, latency, and authentication
- Data freshness, gaps, revisions, and quality
- Cache usage, storage pressure, reclamation, and capacity trends
- Extension compatibility, health, and resource use
- Backtest and paper-engine status
- Paper-account reconciliation
- ML drift, evaluation, and deployment health
- LLM cost, latency, grounding, schema, and tool failures
- Authentication, secret-vault, trust-store, and certificate health
- Backup status, restore verification, and recovery-objective risk
- Scheduled analysis and notification delivery

Health states include healthy, degraded, blocked, recovering, and unavailable. User-facing findings explain impact and link to affected resources, remediation guidance, and runbooks.

### 28.2 Structured telemetry

OSCA produces structured logs, metrics, traces, job events, and audit records. Correlation identities connect API requests, retrieval jobs, analysis graphs, model inference, order intents, and journal events.

Health checks distinguish component availability from analytical correctness.

### 28.3 Alerts and notifications

Operational alerts support configurable thresholds, grouping, deduplication, suppression, acknowledgement, escalation, and recovery notices. Background-job failures cannot remain silent.

OSCA includes a built-in notification inbox and supports pluggable destinations such as email, messaging systems, webhooks, and operating-system notifications.

### 28.4 Security and privacy

Secrets, sensitive payloads, prompts, and licensed data are redacted according to policy. Audit records are distinct from diagnostic logs and receive stronger integrity and retention controls.

Diagnostic bundles preview included content before export.

### 28.5 External observability

Advanced deployments may export telemetry through open, documented interfaces. External observability is optional and cannot be required for understanding the basic health of a local installation.

## 29. Scheduling and durable workflows

### 29.1 Embedded scheduler

OSCA manages schedules and durable workflow runs internally while allowing external schedulers and automation to invoke the same capabilities through the CLI or API.

Triggers include:

- Fixed time and interval
- Calendar expression
- Exchange-session events
- Before or after market open or close
- Data arrival or revision
- Cache invalidation or detected gap
- Upstream workflow completion
- Threshold or analytical event
- Manual invocation
- External webhook or API request

Time-based triggers declare timezone and daylight-saving behavior. Market triggers use explicit exchange calendars, while cryptocurrency schedules support continuous 24/7 operation.

### 29.2 Durable workflow semantics

Every workflow and run has a stable typed identity. Unrelated workflow types cannot share ambiguous latest-run state.

Workflows declare typed inputs, outputs, dependencies, input revisions, idempotency, concurrency behavior, checkpoints, and resource requirements.

Concurrency policies include allow, queue, replace, and reject. Long-running work supports progress, pause, resume, cancellation, safe shutdown, and resumability where possible.

### 29.3 Failure and missed-run behavior

Retries depend on error category and use provider-aware backoff and quota handling. Work requiring intervention enters a visible blocked or dead-letter state.

Missed-run policies include skip, run once, bounded catch-up, and require approval. Recovery cannot automatically replay financially meaningful paper actions.

### 29.4 Resource and notification controls

Schedules respect configurable CPU, memory, storage, provider quota, and monetary budgets. Priorities prevent lower-value background work from blocking critical operations.

Notifications support grouping, batching, and digest policies so routine successful executions do not overwhelm users.

Imported schedules remain disabled until reviewed. Run history retains lineage, status transitions, resource use, and structured diagnostics.

The initial modular monolith may add optional execution workers later without requiring distributed deployment.

## 30. Deterministic risk policies

### 30.1 Policy hierarchy

OSCA applies versioned deterministic risk policies at:

1. System safety
2. Paper account
3. Portfolio or mandate
4. Strategy
5. Final order-intent validation

The strictest applicable constraint wins. Models and LLMs may propose actions or sizes but cannot approve their own exceptions.

System safeguards include non-bypassable operational invariants. Account and portfolio policies cover capital, currency, universe, exposure, concentration, liquidity, drawdown, and loss constraints. Strategy policies add method-specific sizing, turnover, holding-period, and order restrictions.

### 30.2 Shared enforcement

The authoritative event-driven backtest and paper-trading engine use the same risk-policy domain and evaluation behavior. Vectorized research may approximate supported policies but must disclose omissions or semantic differences.

Risk evaluation occurs before strategy action where applicable, before order acceptance, and after fills or material portfolio events.

### 30.3 Risk controls

Controls include, as applicable:

- Maximum position size
- Gross and net exposure
- Leverage
- Cash reserve
- Asset-class and sector concentration
- Correlated exposure
- Turnover
- Liquidity and estimated market impact
- Spread and slippage
- Drawdown
- Daily and cumulative loss
- Stale, partial, provisional, or low-quality data
- Provider, accounting, reconciliation, certificate, storage, and operational health
- Stop-loss, take-profit, trailing-stop, and time-exit policies

Stops are simulated execution instructions and do not guarantee a fill price. Initial paper accounts use no leverage by default.

### 30.4 Decisions, overrides, and safety actions

Risk outcomes are structured and explain approval, modification, rejection, or pause. Risk breaches create findings and alerts and may pause further paper orders.

OSCA provides account-level pause and a system-wide paper-automation kill switch. Overrides require explicit authority, rationale, scope, duration, and audit history.

Policy versions are pinned to backtests and retained paper decisions. Policy changes affect future decisions unless an explicit reevaluation is requested.

Stress and scenario analysis evaluates adverse price, volatility, correlation, liquidity, and provider-failure conditions.

## 31. Price adjustments and instrument lifecycle events

### 31.1 Canonical raw observations

OSCA preserves raw provider price and volume observations. Adjusted values do not overwrite raw observations.

Provider-adjusted series and adjustment factors may be retained with explicit provider provenance for comparison and validation.

### 31.2 Lifecycle events

Equity lifecycle and corporate-action events include, as applicable:

- Splits and reverse splits
- Cash and stock dividends
- Spin-offs
- Mergers and acquisitions
- Rights
- Listing and venue changes
- Symbol changes
- Suspensions and delistings

Events preserve announcement, ex-date, record, payable, effective, and information-availability timestamps where relevant.

Crypto-specific events include redenominations, token migrations, forks, airdrops, symbol changes, and material network lifecycle changes through analogous typed events rather than equity-only semantics.

### 31.3 Versioned adjustment views

OSCA supports explicitly selected price views:

- Raw traded prices
- Split-adjusted prices
- Split-and-distribution-adjusted prices
- Total-return series
- Identified provider-defined adjusted series

Every adjusted result identifies its methodology, event revisions, input datasets, calculation version, and volume-adjustment behavior. Analyses, indicators, and charts disclose the selected view. Incompatible adjustment policies cannot be joined silently.

### 31.4 Backtesting and revision behavior

Event-driven backtests use raw tradable prices and apply corporate actions as explicit portfolio and accounting events. Total-return benchmarks may use adjusted series with visible semantics.

Point-in-time tests use only lifecycle information available at simulated time. Revised or late events create new dataset revisions and identify affected analyses, models, and backtests.

## 32. Data-quality framework

### 32.1 Quality states

Datasets and revisions receive structured quality state:

- Valid
- Valid with findings
- Degraded
- Partial
- Quarantined
- Invalid
- Superseded

Workflows declare the severities and conditions they accept. Exploratory views, ML training, backtesting, and paper automation may apply increasingly strict gates.

### 32.2 Validation scope

Versioned and context-aware quality rules cover, as applicable:

- Schema and required fields
- Canonical instrument mapping
- Timestamp ordering, uniqueness, timezone, session, and calendar alignment
- OHLC invariants
- Price, volume, unit, scale, and currency validity
- Missing, unexpected, duplicate, or overlapping intervals
- Extreme movement and stale-value detection
- Corporate actions and adjustment factors
- Provider revisions and discontinuities
- Cross-provider discrepancies
- Fundamental reporting periods
- News duplication and publication timing
- Future information and look-ahead contamination
- Feature leakage and label alignment

Rules account for market, venue, asset class, interval, provider semantics, and lifecycle state.

### 32.3 Findings and repair

Quality findings include severity, rule identity and version, affected scope, evidence, impact, and suggested remediation.

Automatic repairs are deterministic versioned transformations that create new revisions. OSCA never silently interpolates values, removes outliers, shifts timestamps, changes units, or remaps symbols.

Original source data, prior canonical revisions, repair transformations, and affected downstream artifacts remain traceable. Material repairs support preview and approval.

Provider comparison informs quality findings but does not automatically identify one provider as truth.

### 32.4 Downstream enforcement

Every analysis records its accepted quality policy and actual findings. Quality regression triggers dependency-aware impact analysis.

Paper automation rejects inputs violating active risk or quality policy. LLMs may explain findings and propose remediation but cannot silently modify canonical data.

Quality dashboards show trends by provider, instrument, interval, rule, severity, and revision.

## 33. Data-source access and licensing governance

### 33.1 Supported acquisition mechanisms

OSCA supports governed acquisition through:

- Open public APIs
- Authenticated free or paid APIs
- User-authorized account exports
- Downloaded datasets and files
- Licensed feeds
- Provider-supported webhooks or streams
- Permitted browser or workflow automation
- User-supplied data
- Independently distributed provider extensions

Official APIs and exports are preferred when available. Automation cannot bypass authentication, paywalls, access controls, CAPTCHAs, rate limits, or technical restrictions.

User credentials authorize only the access allowed by the user's provider entitlement.

### 33.2 Provider policy metadata

Provider definitions record, where known:

- Terms and policy references
- License and attribution
- Authentication model
- Rate limits and quotas
- Permitted caching and retention
- Permitted transformation
- Export and backup restrictions
- Redistribution and commercial-use restrictions
- Effective date and review status

Policy metadata is versioned. Uncertainty creates visible warnings and can block persistence, export, backup inclusion, or redistribution.

### 33.3 Enforcement and lineage

Raw retention can be disabled while transient processing remains permitted. Projects, backups, exports, reports, extensions, and shared artifacts enforce applicable restrictions.

Derived outputs retain license lineage where restrictions continue to apply. Required attribution remains attached.

Quotas and rate limits are enforced centrally across concurrent workflows. Provider health includes access-method stability and policy-review state.

Provider adapters degrade safely when access methods or terms change. Users can configure legitimate choices but cannot disable provider restrictions.

OSCA does not grant rights to third-party data. Commercial or multi-user deployment requires a separate provider-license review.

## 34. Primary research lifecycle

OSCA provides a guided but non-linear lifecycle. Users may revisit, branch, compare, or skip stages when applicable requirements and promotion gates permit.

### 34.1 Configure

Establish secure deployment, providers, credentials, storage, resource budgets, recovery, and notifications.

### 34.2 Frame

Create a project and record its objective, investment horizon, hypotheses, assumptions, constraints, and success criteria.

### 34.3 Define

Select or create the instrument universe, benchmarks, intervals, provider policies, data requirements, and quality gates.

### 34.4 Acquire and validate

Resolve cached data, retrieve missing ranges, inspect provenance, address quality findings, and pin dataset revisions.

### 34.5 Explore

Visualize markets, calculate metrics, compare instruments, investigate events, and form observations.

### 34.6 Compose and evaluate

Build analysis graphs, generate signals and findings, and evaluate historical outcomes.

### 34.7 Model

Define features and labels, train candidates, run evaluations, and compare ML methods against appropriate baselines.

### 34.8 Backtest

Perform vectorized research, robustness analysis, and authoritative event-driven validation.

### 34.9 Review and promote

Review evidence, contradictions, assumptions, risk, data quality, and promotion gates. A successful-looking backtest cannot automatically activate paper trading.

### 34.10 Paper deploy

Connect an explicitly approved strategy or recommendation policy to a paper account under deterministic risk rules.

### 34.11 Monitor

Track data and operational health, thesis state, model drift, portfolio risk, execution differences, costs, and recovery posture.

### 34.12 Learn

Compare expected and realized outcomes, document findings, revise hypotheses, and create subsequent experiments.

### 34.13 Report and preserve

Generate evidence-backed reports, export or archive projects, and retain reproducibility manifests.

### 34.14 Lifecycle experience

Each stage exposes prerequisites, outputs, unresolved findings, and recommended next actions. Material assumption changes can branch a project.

The web interface offers both lifecycle guidance and direct expert-tool access. CLI and API workflows use the same stage and gate concepts without requiring an interactive wizard.

Templates are inspectable and editable. Ad hoc exploration can be promoted into a governed project with captured dependencies. The project timeline records decisions, dataset revisions, experiments, promotions, and outcome reviews.

LLM assistance remains context-aware and bounded at every stage.

## 35. Product success scorecard

OSCA measures success through rigorous, reproducible, safe, and efficient research rather than promising financial returns.

### 35.1 Research integrity

Measures include:

- Complete lineage coverage for retained results
- Reproduction success
- Point-in-time and leakage-control compliance
- Baseline-comparison coverage
- Structured evidence, contradiction, horizon, and invalidation coverage
- Outcome-evaluation completion

### 35.2 Data and cache effectiveness

Measures include:

- Avoided duplicate retrieval
- Targeted-repair success
- Quality-finding detection and resolution
- Provider-fallback transparency
- Storage-budget adherence
- Recoverability of evicted derived data

### 35.3 Backtesting and model quality

Measures include:

- Completion of event-driven and out-of-sample validation before promotion
- Calibration, stability, and regime robustness
- Difference between research estimates and event-driven results
- Difference between backtests and forward paper outcomes
- Champion and challenger evaluation completeness

### 35.4 Safety and correctness

Measures include:

- Paper-account reconciliation
- Unauthorized risk-policy bypass
- Silent canonical-data mutation
- Secret disclosure
- Risk and data-quality gate effectiveness
- Post-recovery reconciliation

The intended targets for unexplained accounting discrepancies, unauthorized bypasses, silent canonical mutations, and secret disclosure are zero.

### 35.5 Operational robustness

Measures include:

- Durable-job success and recovery
- Failure visibility
- RPO and RTO compliance
- Backup verification and recovery-exercise success
- Storage-pressure remediation
- Time to diagnose and recover

### 35.6 User effectiveness

Measures include:

- Time to first governed analysis
- Time to reproduce a project
- Time to compare candidates
- Alert review or intentional suppression
- Completion of core workflows without direct database access
- Documentation-assisted task completion

### 35.7 Extensibility

Measures include:

- Time and code required to add providers or analytical capabilities
- Extension conformance
- Version compatibility
- Operation without privileged internal access

Financial returns remain strategy-evaluation metrics, not product promises or primary product KPIs. Negative results are valuable when they correctly invalidate weak hypotheses.

Milestones define measurable thresholds that tighten over time. Product-health measurement can remain local; external usage telemetry is opt-in. Metric definitions and calculation versions are governed and reproducible.

## 36. Availability, performance, scale, and cost

### 36.1 Reference deployment profiles

| Profile | CPU | Memory | Free storage | Intended use |
|---|---:|---:|---:|---|
| Minimum | 4 modern cores | 8 GB | 20 GB | Daily research and small watchlists |
| Recommended | 8 cores | 16 GB | 100 GB | Daily and selected intraday research, backtesting, and local operation |
| Heavy research | 16 or more cores | 32 GB or more | 500 GB or more | Larger intraday universes, parallel experiments, and local models |

GPU acceleration is optional. Core market data, deterministic analytics, backtesting, cache management, and paper accounting cannot require a GPU.

### 36.2 Initial scale targets

On recommended hardware, OSCA targets:

- At least 50,000 canonical instruments and provider mappings
- Twenty years of daily bars for at least 10,000 instruments
- Configurable one-minute histories for at least 500 selected instruments, subject to storage policy
- Larger universes at coarser intervals without loading complete datasets into memory
- At least four independent background jobs while retaining interactive responsiveness
- Hundreds of analytical capabilities and extensions without eager loading
- Thousands of retained experiments and backtests through indexed metadata and lazy artifact access
- Priority for paper-account processing over exploratory work

### 36.3 Responsiveness objectives

For cached and indexed data on recommended hardware:

- Common navigation and metadata operations: p95 under one second
- Typical dashboards and charts: p95 under three seconds
- Job submission acknowledgement: under one second
- Health, job, and paper-account state visibility: within five seconds
- Cancellation acknowledgement: within two seconds before safe termination
- Long-running work exposes progress or a meaningful phase within two seconds

Provider latency is excluded from application-processing targets but remains visible.

### 36.4 Reference computational objectives

Using governed benchmark datasets on recommended hardware:

- F0 signal study across twenty years of daily data for 1,000 instruments: target under two minutes
- F1 ten-year daily portfolio estimate over 500 instruments: target under two minutes
- F2 five-year daily event-driven simulation over 100 instruments: target under ten minutes
- Resampling and common indicator calculation are incremental when unaffected history already exists

Architecture milestones establish repeatable benchmarks. Targets may be refined only through recorded evidence and an explicit decision.

### 36.5 Availability and isolation

Local mode makes no artificial high-availability claim; recovery and integrity take priority.

Personal-server software targets 99.5 percent availability while the host, storage, and required dependencies are healthy. Provider outages are measured separately.

A job, extension, or provider failure cannot make unrelated capabilities unavailable. Scheduled paper workflows fail safe when required dependencies are unhealthy.

### 36.6 Cost control and graceful degradation

OSCA requires no mandatory paid cloud service. Paid data and model providers remain optional.

Users configure storage, compute, provider quota, LLM token, and monetary budgets. Workflows estimate cost where possible and stop predictably at limits.

Resource pressure pauses or reduces noncritical work. OSCA cannot silently reduce analytical correctness, fidelity, data quality, or security to remain within budget.

Single-node scaling is preferred initially. Optional workers or service extraction require profiling evidence and a recorded architectural decision.

## 37. Risk governance

### 37.1 Living risk register

OSCA maintains version-controlled risks with:

- Stable identity and category
- Description and affected capabilities
- Likelihood and impact
- Leading indicators and triggers
- Preventive and detective controls
- Contingency and recovery
- Residual risk
- Owner and review date
- Related requirements, decisions, tests, controls, and incidents
- Status: open, accepted, mitigated, transferred, avoided, or realized

Criticality considers likelihood, impact, and demonstrated control effectiveness. Security, accounting, data integrity, and unauthorized live execution are critical by default.

Milestones identify risks they introduce or reduce and cannot close while an applicable critical risk lacks accepted treatment and evidence.

Risk acceptance requires explicit rationale, residual impact, owner, and expiration or review date. Realized risks become incident records with corrective action.

The register is reviewed before milestone approval and at least quarterly during active development.

### 37.2 Initial product risks

| Risk | Primary treatment |
|---|---|
| Scope expansion delays a usable product | Vertical milestones, explicit non-goals, gates, and deferred-capability register |
| Architecture becomes over-generalized | Modular monolith, evidence-based extraction, and working vertical slices |
| Provider access or terms change | Capability routing, adapters, policy metadata, fallback, and monitoring |
| Data licensing prevents persistence or export | License-aware catalog and enforcement plus separate commercial review |
| Symbol mapping corrupts datasets | Canonical identities, time-aware mappings, ambiguity quarantine, and audits |
| Poor or revised data invalidates results | Quality gates, immutable revisions, impact analysis, and reproducible reruns |
| Look-ahead or survivorship bias inflates performance | Point-in-time contracts, historical universes, leakage tests, and fidelity promotion |
| Overfitting or regime instability | Baselines, held-out periods, walk-forward tests, robustness, and paper monitoring |
| LLM hallucination influences decisions | Structured evidence, bounded tools, validation, citations, and deterministic risk |
| Prompt injection from external content | Untrusted-content boundaries, permissions, adversarial evaluation, and disclosure control |
| Malicious or defective extension compromises OSCA | Trust tiers, manifests, integrity, conformance, isolation, and kill controls |
| Credentials or private data are exposed | Vault-backed secrets, authenticated transport, redaction, scanning, and scopes |
| Paper-account state becomes inconsistent | Immutable balanced journal, reconciliation, projections, and recovery checks |
| Storage growth destabilizes the host | Budgets, tiered retention, forecasting, safe eviction, and ingestion pause |
| Duplicate or replayed work changes paper state | Typed identities, idempotency, durable state, and explicit recovery policies |
| Provider or network outage causes unsafe action | Freshness and health gates, fail-safe pause, and visible degradation |
| Backups cannot restore | Isolated restores, DR exercises, integrity checks, objectives, and off-device copies |
| Notifications become noise | Deduplication, digests, severity, acknowledgement, and suppression |
| Upgrades change retained results | Immutable versions, lockfiles, deployment pointers, and explicit migration |
| Complexity reduces maintainability | Standards, SDD, IDD, TDD, bounded modules, documentation, and fitness tests |
| Performance misses single-node targets | Benchmarks, profiling gates, incremental work, budgets, and optional workers |
| Users mistake research for guaranteed advice | Explicit uncertainty, methodology, boundaries, and no-return promises |
| Future live execution leaks into initial scope | Explicit non-goal, absent live-order capability, and isolated future seams |

## 38. Engineering-quality direction

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

## 39. PRD sections pending discovery

The following areas are intentionally incomplete:

- Milestone decomposition

## 40. Document governance

Accepted decisions are recorded in [decision-log.md](decision-log.md). A decision remains active until explicitly superseded. Open questions should not be silently converted into requirements.

Detailed architecture and technology selection are deferred until the relevant product requirements and quality attributes are accepted.
