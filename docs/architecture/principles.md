# OSCA Architecture Principles

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval roles:** Product authority, security authority, and quality authority where applicable
- **Purpose:** Convert approved product principles and architecture decisions into durable, testable constraints for specifications and implementation.
- **Authoritative sources:** PRD sections 1, 4–6, 9, 11–17, 22–33, and 35–40; decisions D-001 through D-047; ADR-0001; ADR-0002
- **Downstream consumers:** Module catalog, dependency rules, public seams, technology decision criteria, specifications, tests, reviews, CI gates, and operational documentation
- **Review triggers:** Product or ADR change, architecture exception, milestone entry or exit, security incident, failed recovery, or contradictory implementation evidence

## Interpretation

These principles are architecture constraints, not slogans. Each principle must influence design, verification, or review. A specification that cannot explain how applicable principles are satisfied is incomplete.

When principles appear to conflict, higher-level product authority governs. The design must document the tradeoff rather than silently weakening one principle.

## P-01 — Authority and intent remain traceable

**Rule:** Material behavior and architecture must trace to approved product authority, intent, specifications, acceptance criteria, verification, documentation, ADRs, and risks as applicable.

**Implications:**

- Implementation cannot become the de facto specification.
- Architecture exceptions require explicit rationale and affected traceability.
- Generated documentation or schemas supplement rather than replace governed intent and conceptual guidance.

**Verification:** Traceability checks detect orphan requirements, unlinked specifications, undocumented behavior, and stale authority references.

## P-02 — Deterministic components own financial and governance authority

**Rule:** Market-data normalization, quantitative calculations, portfolio accounting, backtesting, risk enforcement, data-quality rules, cache validity, artifact identity, and promotion gates do not depend on generative judgment.

**Implications:**

- ML and LLM outputs are predictions, interpretations, evidence, or recommendations.
- Numerical claims from generated content must be checked against authoritative calculations.
- Models and extensions cannot approve exceptions to controls governing their own outputs.

**Verification:** Conformance and property tests prove deterministic behavior for equivalent inputs, versions, and configuration.

## P-03 — Evidence and provenance precede recommendation

**Rule:** Every material conclusion or simulated action remains connected to exact evidence, data revisions, transformations, models, parameters, policies, and execution context.

**Implications:**

- Opaque scores cannot replace structured results and contradictions.
- Provider selection, fallback, approximation, quality, and missing data remain visible.
- Reports and visualizations retain reproduction metadata.

**Verification:** Retained outputs can produce a complete lineage and evidence report or explicitly identify unavailable payloads and reconstruction requirements.

## P-04 — Capability modules own meaning, rules, and state

**Rule:** The system is decomposed primarily by cohesive product and operational capabilities, with one authoritative owner for each concept, invariant, and mutable record.

**Implications:**

- Other modules use published contracts or explicit replicated read models.
- Shared mutable domain models and private persistence access are prohibited.
- DDD patterns are applied where semantic or invariant complexity justifies them.

**Verification:** The module map, dependency graph, ownership catalog, and architecture fitness evidence remain consistent.

## P-05 — Local-first and single-owner are real constraints

**Rule:** Core product value must operate under the owner’s control without mandatory paid cloud services, multi-tenancy, or cross-installation synchronization.

**Implications:**

- Workstation and personal-server modes share one logical product model.
- Local mode remains safe and understandable without external infrastructure.
- Future hosted or multi-user compatibility cannot inject initial identity, billing, organization, or distributed-consistency complexity.

**Verification:** Required workflows run in a supported local environment, while personal-server differences are limited to declared transport and operational concerns.

## P-06 — Clients share versioned application capabilities

**Rule:** Web, CLI, API, notebooks, LLM tools, external automation, and workers invoke shared application capabilities with consistent validation, security, provenance, errors, and observability.

**Implications:**

- Presentation clients do not implement authoritative business rules independently.
- Direct database access is not a supported normal workflow.
- Local transport optimization cannot change observable semantics.

**Verification:** Contract tests exercise equivalent behavior through applicable interfaces.

## P-07 — Identity is typed, immutable, and context-aware

**Rule:** Instruments, datasets, revisions, artifacts, workflows, runs, models, extensions, policies, and paper records use stable typed identities. Mutable aliases never become primary identity.

**Implications:**

- Provider symbols are aliases through explicit mappings.
- `latest` resolves to an immutable typed object.
- Unrelated workflow or artifact categories cannot share ambiguous resolution state.

**Verification:** Identity collision, alias resolution, lifecycle, and historical-reference tests cover negative and migration cases.

## P-08 — Revision and append-only history replace silent mutation

**Rule:** Material corrections create new revisions, reversals, replacement entries, or superseding records while preserving history.

**Implications:**

- Source payloads are immutable.
- Canonical corrections and repairs create dataset revisions.
- Paper accounting uses append-only balanced journal records.
- Model, prompt, extension, and policy upgrades do not reinterpret historical outputs.

**Verification:** Audit and reconstruction tests prove that prior states and decisions remain explainable.

## P-09 — Public seams are narrower and more stable than internal collaboration

**Rule:** Provider, analysis, visualization, model, extension, and application interfaces expose minimum typed capabilities required for independent use and compatibility.

**Implications:**

- Public contracts do not expose private storage or internal domain representations.
- Compatibility, versioning, errors, permissions, provenance, and conformance are part of each seam.
- Internal refactoring remains possible without breaking extension consumers.

**Verification:** Consumer-driven contract and conformance tests run against supported contract versions.

## P-10 — Security defaults fail closed

**Rule:** Unsafe exposure, invalid identity, untrusted certificates, missing authorization, invalid integrity, and unapproved permissions deny or pause the operation rather than silently reducing protection.

**Implications:**

- Local binding defaults to loopback or a protected local channel.
- Non-local transport is encrypted and authenticated.
- Secrets remain outside logs, portable artifacts, diagnostics, and extension access.
- Installation does not imply extension activation or permissions.

**Verification:** Negative security tests cover invalid identity, certificate, secret handling, permission, replay, and unsafe-configuration cases.

## P-11 — Untrusted code and content remain bounded

**Rule:** Provider payloads, news, filings, web text, model output, and extension output are treated as untrusted input. Imported executable code receives only declared and approved capabilities.

**Implications:**

- External text cannot become privileged LLM instruction.
- Extensions cannot access internal databases, the secret vault, or unrelated application state.
- Unsafe models or packages may be quarantined.

**Verification:** Injection, sandbox or isolation, permission, schema, resource, and corruption-containment tests are risk-based release requirements.

## P-12 — Failures are isolated, explicit, and recoverable

**Rule:** A provider, extension, model, analysis, job, notification, or optional subsystem failure cannot silently corrupt or make unrelated capabilities unavailable.

**Implications:**

- Partial, stale, blocked, invalid, degraded, and unavailable states are explicit.
- Retry, fallback, missed-run, and cancellation behavior is categorized and visible.
- Financially meaningful actions are never automatically replayed after uncertain failure.

**Verification:** Fault-injection and recovery tests prove containment and visible degraded behavior.

## P-13 — Long-running work is durable and observable

**Rule:** Acquisition, analysis, training, backtesting, backup, restore, migration, and other long-running operations use stable run identities and expose progress, cancellation, diagnostics, resource use, and safe recovery behavior.

**Implications:**

- Background workers execute application capabilities.
- Workflows declare idempotency, concurrency, checkpoints, and missed-run semantics.
- A process restart does not erase the meaning or outcome of durable work.

**Verification:** Restart, resume, cancel, duplicate-request, and blocked-run tests are defined per workflow risk.

## P-14 — Consistency follows invariants, not convenience

**Rule:** Transaction and consistency boundaries are chosen from domain invariants, recovery requirements, and failure consequences. Cross-module atomicity is exceptional and justified.

**Implications:**

- One physical database cannot be used to erase module ownership.
- Cross-module workflows may use application orchestration, events, checkpoints, compensating actions, or explicit consistent-snapshot coordination.
- Read-model lag and failure semantics are declared.

**Verification:** Specifications state consistency needs and tests cover interruption at every material boundary.

## P-15 — Storage is governed product state

**Rule:** Cache, canonical data, derived data, artifacts, journals, and metadata have explicit identity, availability, retention, lineage, licensing, integrity, and recovery semantics.

**Implications:**

- Storage budgets are bounded and configurable.
- Cleanup is scoped, previewable, dependency-aware, and dry-runnable.
- Catalog metadata survives payload eviction.
- Protected content cannot be automatically reclaimed.

**Verification:** Storage-pressure, interrupted-cleanup, relocation, corruption, eviction, and reproduction tests are mandatory by applicable milestone.

## P-16 — Reproducibility is the default lifecycle

**Rule:** Analyses, models, backtests, reports, and paper decisions pin exact data, revisions, definitions, code or build, extensions, models, prompts, policies, calendars, parameters, and environments as applicable.

**Implications:**

- Upgrades do not silently alter retained work.
- Reproducibility manifests are durable project material.
- Random behavior declares seeds and nondeterministic limitations.

**Verification:** Reference workflows reproduce within declared tolerances or provide a structured explanation of unavailable dependencies.

## P-17 — Resource limits degrade capacity, not correctness or security

**Rule:** Storage, compute, quota, token, latency, and monetary budgets fail predictably. OSCA cannot silently reduce analytical correctness, fidelity, data quality, provenance, or security to stay within budget.

**Implications:**

- Lower-priority work pauses before critical paper, recovery, or governance work.
- Approximation and downsampling are explicit and scoped.
- Optional capabilities can become unavailable without weakening mandatory controls.

**Verification:** Budget-exhaustion tests assert ordering, state, alerts, and absence of silent semantic change.

## P-18 — Recovery is proven, not assumed

**Rule:** Backup success is insufficient; OSCA maintains consistent recovery points, isolated restore verification, reconciliation, exercises, objectives, and runbooks.

**Implications:**

- Recovery priority follows declared classes.
- Restore occurs to isolated storage before activation.
- Paper automation remains paused until required safety and accounting checks pass.
- At least one backup copy can leave the active failure domain securely.

**Verification:** Automated integrity checks, monthly isolated restores, quarterly exercises, and recorded remediation evidence are supported by the applicable milestones.

## P-19 — Observability explains impact and action

**Rule:** Logs, metrics, traces, job events, audit records, and health findings are structured, correlated, privacy-aware, and connected to user impact and remediation.

**Implications:**

- Availability and analytical correctness are distinct health dimensions.
- Audit records receive stronger integrity treatment than diagnostic logs.
- Local users do not require external observability infrastructure to understand basic health.

**Verification:** Operational scenarios demonstrate detection, correlation, explanation, alerting, runbook linkage, and recovery notice.

## P-20 — Documentation and accessibility are completion criteria

**Rule:** Usage, methodology, operations, security, extension, migration, limitations, troubleshooting, and accessibility documentation ship with affected behavior.

**Implications:**

- Generated references alone are insufficient.
- Examples and commands are executable or validated where practical.
- Visual behavior supports keyboard, screen reader, non-color encoding, and accessible summaries as applicable.

**Verification:** Documentation, example, accessibility, and version-match checks are milestone exit evidence.

## P-21 — Technology decisions follow requirements and evidence

**Rule:** Language, persistence, frontend, ML, deployment, packaging, and isolation technologies are selected only after decision criteria, constraints, alternatives, tradeoffs, migration, and fitness evidence are defined.

**Implications:**

- Familiarity alone is not sufficient rationale.
- Architectural spikes are allowed only to resolve genuine uncertainty.
- Technology choices cannot weaken accepted requirements.

**Verification:** Each consequential selection has an accepted ADR and linked evaluation evidence.

## P-22 — Distribution is earned by evidence

**Rule:** Single-node modular-monolith deployment is the default. Optional workers or service extraction require profiling, isolation, scaling, deployment, security, or organizational evidence and a new ADR.

**Implications:**

- Modules are not microservices-in-waiting.
- Distributed transactions, service discovery, multi-region behavior, and tenant isolation are not designed prematurely.
- Contracts preserve future options without imposing current operational cost.

**Verification:** Architecture review rejects distribution without measured need and documented migration consequences.

## Exception policy

A proposed exception must include:

- affected principle and authority;
- necessity and rejected alternatives;
- scope and duration;
- risk and security impact;
- compatibility and migration effect;
- verification and rollback evidence;
- approving governing role;
- expiration or revisit trigger.

An exception cannot authorize a product-boundary change. Product changes require product decision governance.
