# OSCA Decision Log

This log records accepted product and architectural-direction decisions made during PRD discovery. Entries capture the rationale current at the time of acceptance. Later changes must supersede an earlier entry explicitly rather than silently rewriting it.

## D-001 — Initial product boundary

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will initially provide research, decision support, backtesting, and paper trading.
- **Rationale:** Paper trading supplies a forward-evaluation feedback loop without exposing real capital to software or model errors. It exercises portfolio and order concepts needed for possible future execution.
- **Consequences:** The initial product requires realistic order and fill simulation, portfolio accounting, and comparison between backtests and forward results.

## D-002 — Live execution

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Live brokerage and exchange execution is excluded from the initial scope, while future execution integrations must remain architecturally possible.
- **Rationale:** Live execution introduces materially greater security, compliance, reconciliation, availability, and financial-risk requirements.
- **Consequences:** Core strategy and portfolio concepts must not depend on a particular broker. No initial component may place orders involving real capital.

## D-003 — Intelligence capabilities

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will support both machine learning (ML) and language models (LLMs).
- **Rationale:** ML is appropriate for quantitative prediction, classification, ranking, and detection. LLMs are appropriate for synthesis, explanation, unstructured-data work, and natural-language interaction.
- **Consequences:** ML and LLM capabilities require distinct contracts, evaluation methods, provenance, and failure handling.

## D-004 — Deterministic authority

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Quantitative calculations, market-data normalization, portfolio accounting, backtesting, cache validity, and risk enforcement will be deterministic.
- **Rationale:** Generative output is unsuitable as the numerical source of truth for financially consequential calculations.
- **Consequences:** AI components consume authoritative calculated data and produce bounded outputs such as scores, predictions, explanations, or recommendations.

## D-005 — AI output status

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** AI outputs are versioned evidence, predictions, interpretations, or recommendations—not authoritative financial facts.
- **Rationale:** Model output carries uncertainty and may change with data, code, configuration, prompts, or model versions.
- **Consequences:** Material AI outputs require provenance, model identity, relevant configuration, timestamps, and evaluation context.

## D-006 — Operating model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will have a local-first core with an optional personal-server deployment.
- **Rationale:** This balances privacy, local experimentation, remote access, scheduled processing, and future product growth without premature multi-tenancy.
- **Consequences:** The core must function on a workstation and be packageable for a personal server. Cached data should permit useful partial offline operation.

## D-007 — Initial application topology

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** The initial system will be a single-user modular monolith with background workers.
- **Rationale:** Strong internal boundaries provide extensibility without the operational and consistency costs of premature microservices.
- **Consequences:** Modules require stable, testable contracts. Service extraction will occur only when justified by scaling, isolation, deployment, or organizational evidence.

## D-008 — Initial tenancy and synchronization

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Initial milestones will not implement multi-tenancy or synchronization between independent installations.
- **Rationale:** Both capabilities add substantial identity, conflict-resolution, security, and operational scope before core product value is proven.
- **Consequences:** Interfaces should avoid unnecessary barriers to later hosted operation, but no early implementation work is allocated to these capabilities.

## D-009 — Artifact resolution

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** A mutable alias such as `latest` may only resolve to an immutable, typed artifact and cannot serve as primary identity.
- **Rationale:** Earlier analytical workflows demonstrated that a shared `latest` pointer can resolve to the wrong workflow output, such as confusing training and scanning artifacts.
- **Consequences:** Artifact lookup must consider artifact type, workflow, version, parameters, and lineage. Runs and outputs require stable identifiers.


## D-010 — Target users and personas

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** The primary persona is a technical individual investor/researcher. An analytical investor and an extension developer are secondary personas.
- **Rationale:** This gives OSCA a coherent local-first user while preserving both an approachable analytical experience and a formal extension ecosystem.
- **Consequences:** Advanced research workflows may span the web UI, CLI, API, and notebooks. Consumer-facing views must explain results clearly, while extensions require documented contracts, validation, compatibility rules, and isolated tests.


## D-011 — Initial market universe

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA's initial default universe includes US-listed common stocks, US-listed ETFs, and major spot cryptocurrencies and pairs.
- **Rationale:** This provides strong initial research coverage, useful benchmarks, and both session-based and 24/7 markets while keeping early data and market-structure complexity bounded.
- **Consequences:** Derivatives, foreign exchange, bonds, and non-US equities are excluded from the initial default universe. The domain model must nevertheless remain globally capable.

## D-012 — Extensible instruments and canonical identity

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Instruments within supported asset classes can be registered without code changes. OSCA uses provider-neutral canonical instrument identities with explicit provider-symbol mappings.
- **Rationale:** Tickers are neither globally unique nor permanent, and providers frequently use different identifiers or pair notation for the same economic instrument.
- **Consequences:** OSCA requires an instrument registry, provider mapping records, ambiguity detection, capability metadata, lifecycle handling, and provider-assisted or manual registration. Provider symbols are aliases rather than database primary keys.


## D-013 — Initial time-series resolutions

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will support multi-timeframe OHLCV bars from the beginning, initially covering 1d, 1h, 15m, 5m, and 1m intervals where provider availability and use justify them.
- **Rationale:** Daily and intraday workflows must coexist without embedding daily-only assumptions. Bar data provides the required flexibility without prematurely introducing tick and order-book scale.
- **Consequences:** Calendar-aware gap detection, completed-bar semantics, resampling lineage, provider capability reporting, and interval-specific retention are required. Tick, quote, and order-book data are deferred.

## D-014 — Configurable bounded storage

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Cache and artifact storage will have configurable locations, budgets, retention policies, inspection, cleanup, and safe automatic reclamation.
- **Rationale:** Intraday histories, derived datasets, models, and experiments can otherwise consume unbounded disk space and destabilize workstation or personal-server deployments.
- **Consequences:** OSCA must report usage, forecast pressure, support scoped and dry-run cleanup, protect pinned content, and avoid silently deleting inputs required for retained reproducible experiments.


## D-015 — Storage reclamation policy

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use tiered, value-aware retention with protected, canonical, source, derived, and ephemeral storage classes.
- **Rationale:** Age and recent access alone do not capture analytical value, reproducibility needs, provider recovery cost, or the disproportionate size of high-frequency data.
- **Consequences:** Reclamation considers storage class, interval, age, recomputation cost, provider availability, dependencies, and user pinning. Protected records cannot be automatically deleted; lightweight manifests and lineage survive payload eviction; ingestion pauses safely when protected content exhausts the budget.


## D-016 — Multi-provider routing and reconciliation

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA selects data providers through capability-specific ordered routing policies with explicit fallbacks, provenance, and no silent cross-provider merging.
- **Rationale:** Providers differ by coverage, quality, interval, history, freshness, cost, quota, and licensing. A single global provider is unnecessarily limiting, while automatic merging can create inconsistent and irreproducible datasets.
- **Consequences:** Adapters publish capabilities and limitations. Provider transitions remain visible or pass through an explicit versioned reconciliation process. Cross-provider comparisons produce quality findings rather than silently modifying observations. Experiments can pin provider and dataset revision.


## D-017 — Governed data layers

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use four logical data layers—source, canonical, derived, and artifact—with a shared metadata and lineage catalog.
- **Rationale:** Source observations, normalized facts, reproducible transformations, and research outputs have different correctness, revision, retention, and recovery semantics.
- **Consequences:** Retained source payloads are immutable; canonical corrections create revisions; derived results identify transformations and inputs; artifacts reference datasets explicitly; and catalog metadata survives payload eviction. The logical separation does not mandate four physical databases.


## D-018 — Retrieval and freshness model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use policy-driven hybrid retrieval with explicit data requirements, structured resolution status, targeted gap repair, and on-demand, scheduled, dependency-driven, manual, invalidation-driven, or real-time triggers.
- **Rationale:** Fixed TTLs cannot correctly represent immutable history, provisional bars, provider revisions, market sessions, offline research, and workflows with different freshness tolerances.
- **Consequences:** Callers declare freshness and completeness needs. Equivalent concurrent requests share idempotent retrieval jobs. Historical ranges are repaired incrementally. Analyses retain the exact dataset revision used, and cache results expose freshness, partiality, invalidity, availability, and refresh state.


## D-019 — Analysis extensibility and independent distribution

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will combine declarative analysis composition with typed, versioned code-extension contracts. Extensions can be packaged, published, imported, updated, disabled, and uninstalled independently of the OSCA repository.
- **Rationale:** Common analyses should be composable without code, while new analytical and provider capabilities must evolve without requiring inclusion in core application releases.
- **Consequences:** OSCA requires category-specific contracts, manifests, compatibility checks, integrity verification, installation records, dependency and permission declarations, conformance tests, version pinning, impact previews, and reproducible references to exact extension versions.


## D-020 — Extension trust and import policy

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use built-in, verified, local-trusted, and untrusted/quarantined extension tiers. Imports may originate from local bundles, development directories, immutable Git references, digest-pinned package URLs, and a future registry.
- **Rationale:** Independent distribution must support private development and open publishing without treating all executable packages as equally trusted.
- **Consequences:** Installation and activation are separate; manifests declare permissions; credentials are not granted automatically; permission changes require renewed approval; packages and environments are integrity-pinned; and declared dependencies cannot silently install themselves.


## D-021 — Product interface model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will be web-primary, backed by versioned shared application capabilities with first-class CLI, notebook, and LLM integration.
- **Rationale:** A coherent application experience is required without sacrificing automation and quantitative exploration.
- **Consequences:** Business logic is not duplicated in clients; long-running operations use durable jobs; direct database access is unsupported for normal workflows; and CLI coverage prioritizes automation and operations rather than visual parity.

## D-022 — Usage documentation as a release requirement

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Version-matched usage, operations, API, analytical-methodology, and extension documentation is a release-blocking part of OSCA's definition of done.
- **Rationale:** The platform's analytical, data-governance, storage, extensibility, and operational behavior cannot be used safely or effectively without clear documentation.
- **Consequences:** Behavior changes and their documentation ship together. Task-oriented guides, examples, references, runbooks, limitations, and troubleshooting are maintained and validated where practical; generated references alone are insufficient.


## D-023 — Research organization

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will combine a reusable global catalog with isolated research projects and independently managed paper accounts.
- **Rationale:** Shared datasets and extensions should be reusable without allowing mutable global configuration to compromise experiment isolation or portfolio accounting.
- **Consequences:** Projects pin dependencies, contain research intent and outputs, and support clone, archive, comparison, import, and export. Global changes require impact analysis. Reusable content is promoted explicitly. Paper accounts can consume promoted research outputs without belonging to a project.


## D-024 — Analytical output model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will represent observations, signals, findings, theses, recommendations, and alerts as distinct connected result types. Composite scores are optional summaries rather than complete outputs.
- **Rationale:** Facts, method-specific interpretations, testable hypotheses, and proposed actions have different authority and lifecycle semantics. Collapsing them into one score obscures uncertainty and disagreement.
- **Consequences:** Results retain horizon, confidence, evidence, contradictions, assumptions, quality, regime, invalidation, risk, provenance, state, and later outcome evaluation as applicable. LLM narratives cannot replace authoritative structured evidence.


## D-025 — Analysis families and capability packs

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will support market and technical, fundamental and valuation, quantitative and statistical, portfolio and risk, macroeconomic and cross-market, event and catalyst, news and sentiment, crypto-specific, ML, LLM synthesis, and strategy-outcome analysis through versioned capability packs.
- **Rationale:** The product requires broad analytical coverage without coupling every specialist method and data dependency to the core release.
- **Consequences:** A smaller cross-asset analytical foundation ships first. Packs declare data requirements and degradation behavior, use governed contracts and structured outputs, and include methodology, tests, limitations, and usage documentation. Equivalent methods may coexist and be evaluated comparatively.


## D-026 — Visualization extension model

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use versioned declarative visualization specifications rendered by the application, with separately governed custom views for specialized interactions.
- **Rationale:** Analytical extensions need rich presentation without requiring arbitrary frontend code or direct internal-data access.
- **Consequences:** Specifications consume typed results, support interactive dashboards and static rendering, retain provenance, disclose downsampling, export data and reproduction metadata, and meet accessibility requirements. Custom views require additional trust, permissions, and compatibility governance.


## D-027 — Dual-stage backtesting

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will provide fast vectorized research mode and authoritative event-driven simulation mode. Paper trading shares the event-driven domain model.
- **Rationale:** Vectorized evaluation supports efficient exploration but cannot faithfully represent every temporal, order, fill, liquidity, and portfolio behavior required for realistic validation.
- **Consequences:** Strategies declare compatible modes and produce typed decisions or order intents. Research results are labeled estimates. Candidates pass through event-driven validation before paper trading. Cross-engine fixtures, visible result differences, point-in-time enforcement, reproducible assumptions, and promotion gates are required.


## D-028 — Paper-accounting authority

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** Paper accounts will use immutable order events and an append-only double-entry journal as accounting authority, with rebuildable portfolio projections.
- **Rationale:** Mutable balance snapshots cannot fully explain or reconcile cash, positions, fees, corporate actions, multi-currency effects, and corrections.
- **Consequences:** Corrections use reversals; every economic event produces balanced entries; orders and fills retain analytical and market-data lineage; valuations retain price and FX sources; projections and performance snapshots remain regenerable; and tax output is initially analytical rather than authoritative.


## D-029 — Machine-learning lifecycle

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use a governed experiment and model registry with pluggable training workflows, immutable model versions, explicit promotion gates, champion/challenger paper deployment, and drift monitoring.
- **Rationale:** Diverse ML methods require extensible training while model comparison, reproducibility, deployment, and monitoring require consistent lifecycle governance.
- **Consequences:** Training captures exact inputs and environment; features declare temporal availability; baselines are mandatory; evaluation separates selection and held-out periods; retraining does not imply promotion; deployments are reversible pointers; unsafe imports can be quarantined; and RL remains bounded by deterministic risk rules.


## D-030 — Governed LLM gateway

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use a provider-neutral LLM gateway with bounded typed tools, versioned prompts and schemas, structured-output validation, evidence grounding, privacy controls, resource budgets, and dedicated evaluations.
- **Rationale:** Direct provider coupling or broad autonomous access would weaken reproducibility, privacy, cost control, prompt-injection resistance, and deterministic system boundaries.
- **Consequences:** LLMs cannot query internal databases or place live orders; state-changing tools require policy or confirmation; retained workflows pin versions; untrusted content remains data; sensitive disclosure is controlled; and evaluation covers grounding, citations, numerical consistency, tools, injection resistance, task completion, cost, and latency.


## D-031 — Deployment-aware identity and secret security

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use loopback-safe local operation, authenticated personal-server access, scoped automation credentials, internal capability enforcement, and vault-backed secrets.
- **Rationale:** A single-user product still protects valuable credentials, data, models, and portfolio information while local workflows should not incur unnecessary login friction.
- **Consequences:** Network exposure is explicit; remote operations authenticate; automation access is revocable and scoped; extensions and LLM tools receive bounded capabilities; secrets are excluded from logs and portable artifacts; and future multi-user identity requires a deliberate redesign.

## D-032 — Authenticated encrypted network transport

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** All non-local network transfer uses modern encrypted transport, validated server identity, and client authentication. Controlled machine-to-machine channels support or require mutual TLS according to their security profile; external services use the strongest client-authentication mechanism they support.
- **Rationale:** Confidentiality alone is insufficient: OSCA must authenticate remote endpoints and callers, reject invalid trust, and support deployment policies aligned with applicable organizational or regulatory controls.
- **Consequences:** Plaintext and certificate-validation bypasses are prohibited; TLS and trust failures fail closed; credentials rotate and revoke; remote browsers use TLS plus application sessions; remote automation can combine mTLS with scoped credentials; and certificate lifecycle requires health checks, documentation, and runbooks.


## D-033 — Policy-aware backup and disaster recovery

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will provide encrypted lightweight, standard, and archival backup profiles with dependency-aware selective restore, plus a disaster-recovery program with explicit objectives, prioritized restoration, runbooks, off-device capability, automated verification, and recovery exercises.
- **Rationale:** Creating backup files does not establish recoverability. Robust operation requires consistent recovery points, independent copies, validated restore paths, failure-scenario planning, and evidence that recovery objectives can be met.
- **Consequences:** Secrets remain separate; packages report exclusions; restores validate before activation; paper journals and catalogs reconcile; recovery follows declared priority; backup copies can leave the active failure domain securely; and periodic isolated restore tests and disaster-recovery exercises are release and operational requirements.


## D-034 — Tiered recovery objectives

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use tiered RPO and RTO targets, with a default one-hour RPO and four-hour RTO for critical state and an optional hardened 15-minute RPO and one-hour RTO.
- **Rationale:** Paper journals and system identity require substantially stronger recovery than reconstructable market caches or ephemeral data.
- **Consequences:** Active research defaults to four-hour RPO and eight-hour RTO; protected artifacts to 24 hours each; reconstructable payloads have no backup guarantee; objective risk is visible; paper automation remains paused during unsafe recovery; isolated restore tests run monthly; and broader recovery exercises run at least quarterly.


## D-035 — Built-in observability and health

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will provide a built-in operational health center backed by structured logs, metrics, traces, job events, and protected audit records, with optional standards-based external telemetry export.
- **Rationale:** Local deployments need understandable health and remediation without requiring external infrastructure, while advanced personal servers benefit from integration with broader observability systems.
- **Consequences:** Telemetry is correlated across workflows; health separates availability from analytical correctness; alerts deduplicate and report recovery; failures are not silent; sensitive data is redacted; audit retention is stronger than diagnostic logging; and exported diagnostics require preview.


## D-036 — Embedded durable scheduling

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will include an embedded durable workflow scheduler with market-aware, calendar, dependency, data, analytical, manual, and external triggers, while permitting CLI and API invocation.
- **Rationale:** Core local-first workflows require consistent scheduling, dependencies, retries, progress, lineage, and missed-run behavior without mandating an external orchestrator.
- **Consequences:** Workflows have typed identities and inputs; equivalent work deduplicates; schedules declare timezone and market semantics; failures and missed runs follow explicit policies; resources and provider quotas are budgeted; imports remain disabled pending review; and recovery cannot silently replay paper actions.


## D-037 — Layered deterministic risk policies

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will enforce versioned deterministic risk policies at system, paper-account, portfolio, strategy, and final order-intent levels, with the strictest applicable constraint winning.
- **Rationale:** Strategies, ML models, LLMs, and imported extensions cannot be responsible for approving exceptions to their own proposed actions.
- **Consequences:** Event-driven backtests and paper trading share risk semantics; controls cover exposure, concentration, liquidity, loss, data quality, and operational health; decisions are explainable; overrides are scoped and audited; leverage is off by default; and account pause plus a system-wide paper kill switch are required.


## D-038 — Raw prices and versioned adjustment views

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will preserve canonical raw price and volume observations, model corporate actions and crypto lifecycle changes explicitly, and provide versioned selectable adjustment views.
- **Rationale:** Adjusted series are useful for analysis but cannot replace actual historical tradable observations or explicit accounting events.
- **Consequences:** Analyses disclose adjustment policy; incompatible views do not mix silently; event-driven backtests apply actions to raw prices; point-in-time tests enforce information availability; and event revisions create new dataset revisions with impact analysis.


## D-039 — Policy-driven data quality

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use versioned contextual quality rules, explicit validity and degradation states, quarantine, traceable repair revisions, and workflow-specific acceptance policies.
- **Rationale:** Rejecting all imperfect real-world data sacrifices availability, while permissive warnings allow defects to contaminate models, backtests, and recommendations.
- **Consequences:** Quality findings preserve evidence and impact; repairs never silently rewrite data; provider comparison does not automatically establish truth; downstream artifacts retain accepted policy; regressions trigger impact analysis; and paper automation enforces strict risk-linked quality gates.


## D-040 — Governed data acquisition and licensing

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will support open, authenticated, licensed, exported, file-based, user-supplied, and permitted automated data acquisition through versioned provider policy metadata and enforcement.
- **Rationale:** Technical retrievability does not establish permission to retain, transform, export, back up, or redistribute third-party data.
- **Consequences:** Official mechanisms are preferred; automation cannot bypass controls; quotas are centralized; provider rights constrain storage and portability; derived outputs retain applicable lineage; uncertainty can block use; and commercial or multi-user operation requires separate license review.


## D-041 — Guided research lifecycle

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will provide a guided but non-linear lifecycle from secure configuration and research framing through governed data, exploration, modeling, dual-stage backtesting, promotion, paper deployment, monitoring, outcome learning, and preservation.
- **Rationale:** Independent tools provide flexibility but do not ensure that intent, evidence, assumptions, promotion, and realized outcomes remain connected.
- **Consequences:** Stages expose prerequisites and outputs; projects can branch; ad hoc work can be governed later; timelines retain decisions and revisions; the web UI combines guidance with expert access; CLI and API share lifecycle semantics; and LLM assistance cannot bypass gates.


## D-042 — Product success measurement

- **Status:** Accepted
- **Date:** 2026-07-17
- **Decision:** OSCA will use a balanced product scorecard centered on research integrity, data effectiveness, model and backtest rigor, safety, operational robustness, user effectiveness, and extensibility. Financial returns and raw engagement volume are not primary product KPIs.
- **Rationale:** Product correctness is distinct from market outcomes, and activity counts can reward noise, overfitting, and unnecessary complexity.
- **Consequences:** Milestones define measurable outcome thresholds; zero tolerance applies to unexplained accounting discrepancies, unauthorized risk bypass, silent canonical mutation, and secret disclosure; negative research results retain value; telemetry remains local by default; and measurement definitions are versioned.
