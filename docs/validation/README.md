# Architecture Validation

- **Status:** Accepted procedure
- **Milestone:** M0.6
- **Governing role:** Architecture authority
- **Approval roles:** Product, security, and quality authorities for their scopes
- **Purpose:** Define repeatable acceptance validation for the OSCA architecture baseline.
- **Authoritative sources:** ADR-0001 through ADR-0010; verification strategy; architecture fitness program
- **Review trigger:** Baseline change, M1 entry, or validation failure
- **Last reviewed:** 2026-07-18

## Validation sequence

1. Pin the repository revision and validation-manifest revision.
2. Execute every applicable check in [`checks.yaml`](checks.yaml).
3. Record automated output or inspection evidence.
4. Add every failure, ambiguity, or unsupported assertion to the findings table.
5. Close the finding, accept it as governed debt, or assign an owner, trigger, and deadline.
6. Obtain required authority disposition.
7. Update lifecycle state only after the evidence supports it.

## Result semantics

- **Pass:** Evidence satisfies the check.
- **Pass with limitation:** The rule is satisfied, but automation or implementation evidence is intentionally deferred and recorded.
- **Fail:** A governing rule is contradicted or required evidence is missing.
- **Not applicable:** The check does not apply at the pinned revision, with rationale.

A document's existence is not by itself proof of correctness. Inspection is valid evidence for documentation-only baseline checks; implementation claims require executable evidence once implementation exists.

## Evidence retention

Each record identifies source revision, manifest revision, date, executor, method, result, evidence location, findings, exceptions, and approvals. The [M0.x validation record](m0x-validation-record.md) is the initial execution.

## Promotion rule

ADR-0001 through ADR-0010 may move from Accepted to Baseline only when all M0.6 checks pass or have an approved disposition. Frozen state begins only when M1 implementation begins.
