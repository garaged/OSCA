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
