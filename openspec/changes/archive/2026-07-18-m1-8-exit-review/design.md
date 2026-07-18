## Context

M1 slice evidence is complete, but exit authority needs one coherent decision package. The repository still has stale implementation status, incomplete aggregate traceability, un-dispositioned performance budgets and open questions, and mixed contract lifecycle states. OpenSpec tracks the reconciliation; product, architecture, security, and quality authorities decide acceptance.

## Goals and non-goals

### Goals

- Trace every M1 acceptance criterion to executed evidence or an explicit approved limitation.
- Observe the M1 performance budgets in a bounded reference environment.
- Reconcile compatibility, contract support, residual risks, and deferred decisions.
- Produce one integrated exit record with exact source and CI identity.
- Leave repository status and navigation internally consistent.

### Non-goals

- Expand M1 behavior, alter Frozen ADRs, or begin M2.
- Convert reference observations into production-wide guarantees.
- Claim supported operating systems or public-internet hardening without evidence.
- Use OpenSpec to approve the milestone.

## Decisions

### Exit matrix

The exit record uses M1-AC-001–M1-AC-020 as the primary verification index and links, rather than copying, slice evidence. Each row records result, evidence, limitation, and disposition.

### Performance observations

M1-AC-019 is evaluated on the locked reference environment. Measurements are bounded, repeatable observations with environment identity. They confirm or disposition M1 targets but do not establish product-wide SLOs.

### Open-question disposition

Dual-stack binding remains platform-dependent unless target evidence supports a stronger claim. Supported credential-store operating systems remain unclaimed until conformance runs exist. Both receive explicit post-M1 triggers and owners.

### Acceptance boundary

Automated checks can prove technical gates. The exit record remains Proposed until the named product, architecture, security, and quality authorities accept it.

## Risks and tradeoffs

- Benchmark tests can be noisy; use generous specification budgets, repeated samples where useful, and record the environment.
- Status updates can overclaim; perform them only after the matrix and validation pass.
- Historical slice wording can be stale; disposition it in the integrated record rather than rewrite historical evidence.

## Validation

- locked environment, Ruff, strict mypy, and full pytest;
- architecture, migration, schema, contract, compatibility, link, and secret gates;
- bounded startup/readiness/workflow performance observations;
- strict OpenSpec validation;
- complete criterion, requirement, risk, limitation, and deferred-work inspection;
- final PR review at an exact head revision.
