# ADR-0008: Tiered Extension Isolation Model

- **Status:** Baseline
- **Tier:** Foundational
- **Date:** 2026-07-17

## Context

OSCA permits extensions designed and published outside the application repository. Extension execution must balance performance, ecosystem openness, least privilege, and fault containment without binding the architecture to one sandbox technology.

## Decision

Adopt trust-tiered isolation behind an Extension Runtime Seam.

### Tier 1: Core extensions

Core extensions are maintained and released with OSCA, use the same quality gates as the platform, and may execute in-process.

### Tier 2: Trusted partner extensions

Partner extensions are independently versioned, signed, verified, permission constrained, resource governed, and executed with fault isolation from the core platform.

### Tier 3: Community extensions

Community extensions are untrusted by default and execute in a sandboxed runtime. They receive no implicit filesystem, network, secret, model, provider, or persistence access. Capabilities are declared and granted explicitly, with quotas and execution limits.

Every extension declares publisher identity, semantic version, supported contract families and revisions, OSCA compatibility, required permissions, resource expectations, integrity metadata, and signature information. Installation and activation are separate lifecycle operations.

Extensions communicate only through approved public seams and never access capability internals or persistence directly. The host can disable, quarantine, roll back, or uninstall an extension without compromising core availability.

The Extension Runtime Seam owns compatibility validation, loading, unloading, permission enforcement, isolation policy, resource accounting, lifecycle, and health monitoring. The specific runtime or sandbox technology remains replaceable.

## Consequences

First-party performance is preserved while third-party execution receives proportionate containment. The platform must support manifests, signing, explicit grants, health monitoring, and more than one execution mode.

## Rejected alternatives

- All extensions execute in-process.
- All extensions use the same fully isolated execution model.
