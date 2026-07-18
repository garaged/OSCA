# M1.8 Exit Review Gap Analysis

- **Status:** Complete analysis; findings resolved and exit accepted
- **Governing roles:** Product, architecture, security, and quality authorities
- **Requirements:** REQ-0001–REQ-0020
- **Governing specification:** [M1 secure walking skeleton](../../specifications/m1-secure-walking-skeleton.md)
- **Source baseline:** `c16119dbaf19004a92128d9db83f81846d4fd062`
- **Reviewed:** 2026-07-18

## Scope and method

This analysis reconciles the accepted M1 intent, scope, requirements, ADRs, specification, contract catalog, deferred decisions, architecture registry, implementation-slice evidence, documentation, and current repository status. It is an exit-review input, not an acceptance decision. M0 and Frozen Tier-1 ADRs remain authoritative.

## Completed and evidenced

| Exit area | Repository-backed result |
|---|---|
| Increment delivery | M1.1–M1.7 are marked complete and have retained slice evidence. |
| Architecture | The modular-monolith capability boundaries, public seams, owned persistence, and structural checks are implemented without an active architecture exception. |
| Interfaces | Readiness is exposed through shared CLI, API, and web behavior with contract-equivalence evidence. |
| Security | Loopback-safe defaults, fail-closed personal-server prerequisites, trusted local authorization, vault references, redaction, and secret scanning are evidenced. |
| Durable work | Diagnostic identity, lifecycle, idempotency, leases, checkpointing, interruption/resume, cancellation, retry, and result metadata are evidenced. |
| Persistence and compatibility | Retained Alembic migrations, deterministic schemas, versioned contracts, repository ownership, and compatibility rejection behavior are evidenced. |
| Recovery | Consistent encrypted backup, non-mutating verification, explicit preview, isolated restore, malicious-input rejection, and active-state invariance are evidenced. |
| Observability | Correlation, structured logs, OpenTelemetry signals, health findings, job events, and separate audit records are evidenced. |
| Documentation | Version-matched operational guidance, focused diagnostic/recovery instructions, example disposition, links, and CI validation are evidenced. |
| OpenSpec | All applicable M1 changes are validated, synchronized, and archived; no active M1 change remains. |

## Partial or missing exit evidence

| Area | Current state | Exit requirement |
|---|---|---|
| Aggregate traceability | Slice rows are verified, but the broad REQ-0001–REQ-0010/REQ-0016–REQ-0020 row remains **In progress** and points only to incremental evidence. | Reconcile every REQ-0001–REQ-0020 and M1-AC-001–M1-AC-020 link into the final exit record. |
| Performance budgets | The specification defines M1-AC-019 and six observable budgets, but no retained benchmark or explicit budget disposition is linked. | Execute a bounded reference-environment observation or record an authority-approved limitation for each budget. |
| Contract lifecycle | Several implemented families remain **Accepted**, while diagnostic and catalog recovery families are **Supported**. | Confirm conformance evidence and promote implemented M1 families consistently, or explain why a family remains Accepted. |
| Open questions | Dual-stack listener realization and supported credential-store operating systems remain open in the accepted specification. | Resolve or explicitly defer each with trigger, consequence, and authority; do not leave unowned exit ambiguity. |
| Final integrated evidence | Slice evidence exists, but no single exit record reconciles final source, all criteria, risks, compatibility, limitations, and CI identity. | Create and validate an M1 exit evidence/review record. |
| Repository status | `ARCHITECTURE_STATUS.md` and the architecture registry still describe M1 implementation/entry activity. | Update status only after exit findings close and acceptance is justified. |

## Inconsistencies and stale guidance

- `ARCHITECTURE_STATUS.md` says the current activity is M1 implementation and describes unmet M1 entry gates even though M1.1–M1.7 are complete.
- `engineering/architecture-registry.yaml` retains project status `m1-implementation`; no declared post-M1 status exists yet.
- The aggregate traceability row overlaps verified slice rows but still presents the included requirement set as incomplete.
- The technology decision package recommends MkDocs Material and a later OCI personal-server verification profile, while the delivered M1 documentation is repository Markdown and personal-server behavior is a fail-closed configuration skeleton. These recommendations did not become normative ADR obligations, but the exit review must explicitly record the non-adoption/deferment to prevent readers from inferring missing required implementation.
- Early evidence records describe limitations as “later M1” work even where the final specification did not require that hardening. The exit record must disposition them as satisfied elsewhere, residual risk, or post-M1 deferral.

## Duplicate guidance

No new handbook or specification is required. M1.8 should create one review/evidence record and update existing indexes. It must not restate all behavioral requirements or copy slice evidence; use a criterion matrix with links.

## Remaining deliverables

1. Create a bounded M1.8 OpenSpec change for exit reconciliation; OpenSpec tracks work but cannot grant acceptance.
2. Build an M1-AC-001–M1-AC-020 exit matrix linking exact evidence and identifying the AC-019 performance gap.
3. Run bounded performance observations for startup, readiness, submission, visibility/progress, and cancellation on the reference CI/development environment; record limitations rather than converting observations into product-wide guarantees.
4. Reconcile contract lifecycle and compatibility evidence.
5. Disposition both specification open questions and every carried-forward slice limitation/risk.
6. Retain a final integrated source/check/tool/result/exception record.
7. Update traceability, contract catalog, M1 index/execution status, architecture status, and registry only after evidence supports the changes.
8. Review, synchronize, and archive OpenSpec, then rerun all required gates.
9. Obtain the named authority acceptance through the M1 exit review; no automated gate alone grants milestone acceptance.

## Recommended implementation order

1. **Specification:** OpenSpec exit-reconciliation plan and acceptance matrix.
2. **Validation:** add/execute the missing bounded performance observations and inspect compatibility/conformance evidence.
3. **Evidence:** draft the integrated exit record with risks, limitations, open-question dispositions, and exact links.
4. **Governance:** reconcile contracts, traceability, deferred decisions, architecture registry, and milestone indexes.
5. **Review:** run all gates, close findings, archive OpenSpec, and obtain authority acceptance.
6. **Transition:** after acceptance, mark M1 complete and identify the next milestone without implementing M2 scope early.

## Blocking assessment

M1.8 has no discovered architecture redesign requirement, active exception, or failed implementation slice. All identified blockers were resolved: AC-019 has a bounded passing gate, aggregate traceability is verified, specification questions and contract lifecycle are dispositioned, integrated evidence is retained, and the named authorities accepted M1.
