# Architecture Fitness Program

- **Status:** Accepted
- **Scope:** Executable evidence that OSCA continues to satisfy accepted architecture decisions

## Purpose

Architecture documentation is insufficient unless important rules are continuously observable and enforceable. Fitness functions translate accepted ADRs, specifications, quality attributes, and operational policies into automated or explicitly reviewed evidence.

## Fitness categories

### Structure and dependencies

Evidence must detect:

- dependency cycles;
- undeclared module dependencies;
- private implementation imports;
- cross-module persistence access;
- unapproved shared-kernel growth;
- adapters owned by the wrong capability;
- extension dependencies on internal packages.

### Contracts and compatibility

Evidence must verify:

- contract family identity and version metadata;
- producer and consumer compatibility;
- semantic golden fixtures;
- unknown-field and incompatible-major behavior;
- migration and replay correctness;
- product compatibility manifest completeness;
- deprecation and removal policy compliance.

### Determinism and reproducibility

Evidence must control or record clocks, calendars, time zones, seeds, provider responses, dataset revisions, model versions, prompt versions, configuration, and dependency locks where they affect results.

Reference scenarios must prove whether reruns are identical, equivalent within declared tolerances, migrated with provenance, or no longer reproducible for a documented reason.

### Security

Evidence must cover:

- deny-by-default authorization;
- identity and permission boundaries;
- mutual authentication for protected network channels;
- secret leakage prevention;
- audit completeness and redaction;
- extension permission enforcement;
- supply-chain integrity;
- unsafe LLM or model input handling.

### Persistence and recovery

Evidence must exercise:

- schema migration from retained historical states;
- interrupted migration recovery;
- backup restoration;
- integrity verification and reconciliation;
- idempotent workflow resume;
- corrupt or incompatible checkpoint rejection;
- degraded-mode behavior;
- disaster-recovery exercises.

### Performance and capacity

Evidence must maintain representative baselines for latency, throughput, memory, storage growth, concurrency, startup, large datasets, workflow backlog, and extension overhead. Budgets and tolerances are defined by later capability specifications.

### Documentation and governance

Evidence must detect:

- broken links and invalid diagrams;
- missing owners or statuses;
- unindexed ADRs;
- untraced accepted requirements;
- stale exceptions;
- missing contract-catalog entries;
- missing migration, runbook, or security deltas when change classification requires them.

## Execution layers

1. Local fast checks provide immediate deterministic feedback.
2. Pull-request checks enforce the ADR-0005 risk-selected gate set.
3. Scheduled checks execute broader compatibility, security, recovery, and performance suites.
4. Release checks validate the complete supported compatibility and deployment evidence set.
5. Periodic operational exercises validate assumptions that automation cannot fully prove.

## Ownership

Every fitness function has:

- a governing requirement, ADR, risk, or specification;
- an owning capability or governance role;
- a failure severity;
- an execution cadence;
- retained evidence location;
- an exception policy;
- a review date.

Tests without an owner or actionable failure path are incomplete controls.

## Failure policy

A fitness failure blocks the applicable merge or release unless an authorized, expiring exception is recorded under ADR-0005. Failures must identify the violated architectural rule and remediation path, not merely a tool-specific error.

## Evolution

When an incident, defect, review finding, or migration failure reveals an untested architectural assumption, the team adds or strengthens the lowest-cost effective fitness function and links it to the finding.
