# Architecture Evolution and Freeze Policy

## Lifecycle

Governed architecture artifacts use these lifecycle states:

```text
Draft -> Reviewed -> Accepted -> Baseline -> Frozen -> Superseded
```

- **Accepted:** approved and authoritative within its scope.
- **Baseline:** validated as part of an architecture baseline.
- **Frozen:** protected during implementation; changes require supersession.
- **Superseded:** retained as historical evidence and replaced by an explicitly linked artifact.

Rejected and Deprecated remain valid terminal or transitional states where appropriate.

## Baseline and freeze

M0 foundational ADRs become Baseline only after M0.6 architecture validation demonstrates consistency, traceability, owned contracts, and defined fitness obligations. They become Frozen when M1 implementation begins.

Frozen ADRs are not rewritten to conceal architectural evolution. A proposed change creates a new ADR that:

- identifies the superseded decision;
- explains evidence and drivers;
- evaluates compatibility, migration, security, recovery, and operational effects;
- identifies affected requirements, contracts, capabilities, tests, and documentation;
- defines rollout and rollback expectations.

## Review authority

Full architecture review is required for changes affecting foundational ADRs, capability boundaries, new public contract families, extension points, cross-cutting quality attributes, or breaking compatibility.

Routine implementation that conforms to the baseline remains within the owning capability's normal review process.

## Exceptions

Architecture exceptions must be explicit, risk assessed, approved by the proper authority, traceable, narrow in scope, and time limited. An exception does not amend the baseline and must include an expiry or removal trigger.

## Lessons learned

Implementation experience is captured separately from the frozen baseline. Repeated evidence of a structural mismatch may trigger a superseding ADR; isolated inconvenience is not sufficient justification.
