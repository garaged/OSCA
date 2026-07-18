# Resilience and Recovery Baseline

- **Status:** Draft for M0 acceptance
- **Scope:** Technology-neutral operational resilience, backup, restoration, and disaster recovery

## Principles

OSCA must assume that processes stop, hosts fail, networks partition, providers degrade, credentials expire, migrations are interrupted, and stored state can become unavailable or inconsistent.

Recovery is a product capability with tested contracts, not an operator improvisation. Durability claims are valid only when restoration and reconciliation are demonstrated.

## Service objectives

Each capability must eventually declare:

- availability objective;
- maximum tolerable interruption;
- recovery time objective (RTO);
- recovery point objective (RPO);
- degraded-mode behavior;
- dependency assumptions;
- restoration order;
- evidence and review cadence.

Numeric objectives are deferred until workloads and deployment topology are selected. Capabilities must not inherit unsupported objectives implicitly.

## State classification

Durable state is classified as:

1. authoritative domain state;
2. reproducible derived state;
3. externally reacquirable state;
4. operational and audit evidence;
5. ephemeral caches and work products;
6. secrets and trust material.

Each class must define backup, retention, restoration, reconciliation, and deletion behavior. Recomputable state must retain enough provenance and dependency locks to make recomputation credible.

## Backup policy

Backups must be:

- encrypted and access-controlled;
- integrity-checked;
- versioned and retention-governed;
- isolated from ordinary destructive access;
- attributable to a known schema and product compatibility manifest;
- tested through restoration, not merely successful creation;
- capable of supporting point-in-time recovery where required.

Credentials and trust material require separate handling so restoration does not reactivate compromised or expired identities.

## Restoration and reconciliation

A restore procedure must define:

- prerequisites and authorization;
- selected recovery point;
- compatible software and contract versions;
- restoration order and dependency graph;
- integrity validation;
- replay or recomputation steps;
- reconciliation against external providers and retained events;
- audit preservation;
- acceptance criteria and rollback.

Restoration must not silently reinterpret retained artifacts under newer semantics. Any migration performed during recovery must create explicit provenance.

## Workflow durability

Durable workflows must support idempotent restart, checkpoint validation, bounded retry, dead-letter or equivalent failure retention, cancellation, correlation, and operator-visible recovery state.

A workflow may resume only when its definition, inputs, contract versions, permissions, and required dependencies are compatible with the checkpoint. Otherwise it must fail safely or execute an explicit migration.

## Degraded operation

Capabilities must document whether they:

- remain available read-only;
- serve previously verified data;
- queue bounded work;
- reject new work;
- switch providers;
- require operator intervention.

Degraded behavior must be explicit to users and must not present stale, partial, inferred, or unverified output as current authoritative data.

## Disaster recovery

Disaster recovery plans must cover loss or compromise of the primary execution environment, persistence service, artifact store, identity infrastructure, network trust, and critical external provider.

Plans require:

- declared recovery authority;
- protected recovery environment;
- clean-room or equivalent compromise recovery path;
- dependency and contact inventory;
- restoration sequencing;
- data-loss disclosure;
- validation exercises;
- post-recovery credential rotation and reconciliation.

## Operational readiness

A capability is not production-ready until it has:

- health and dependency signals;
- actionable alerts and ownership;
- capacity and saturation indicators;
- operational dashboards;
- failure and recovery runbooks;
- backup/restore evidence where stateful;
- known limits and safe defaults;
- incident correlation and audit support;
- tested rollback or containment.

## Exercises

Recovery exercises must include selected scenarios such as interrupted migrations, corrupt checkpoints, partial provider responses, expired credentials, unavailable dependencies, lost primary persistence, compromised secrets, and restoration from historical backups.

Exercise findings enter the risk or technical-debt register and receive owners and deadlines.
