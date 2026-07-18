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

## 8. Intelligence model

OSCA uses both machine learning and language models, with explicit separation of responsibilities.

### 8.1 Machine learning

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

### 8.2 Language models

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

### 8.3 Deterministic responsibilities

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

## 9. Artifact identity and lineage

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

## 10. Cache and data lifecycle — initial requirements

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

Detailed cache policy remains an open design area and will receive its own specification after product requirements are settled.

## 11. Backtesting and paper trading — initial requirements

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

## 12. Engineering-quality direction

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

## 13. PRD sections pending discovery

The following areas are intentionally incomplete:

- User problems and primary workflows
- Product goals, non-goals, and measurable outcomes
- Market and asset coverage
- Temporal resolutions and operating cadence
- Data-source classes and licensing constraints
- Detailed cache semantics
- Analysis and metric extension model
- Model and experiment lifecycle
- Backtest fidelity levels
- Portfolio and risk functionality
- Visualization and reporting experience
- Alerting and scheduled operation
- Security and credential handling
- Availability, performance, scalability, and cost objectives
- Import, export, backup, and recovery
- Plugin and extension governance
- Milestone decomposition
- Product success metrics
- Risks and mitigations

## 14. Document governance

Accepted decisions are recorded in [decision-log.md](decision-log.md). A decision remains active until explicitly superseded. Open questions should not be silently converted into requirements.

Detailed architecture and technology selection are deferred until the relevant product requirements and quality attributes are accepted.
