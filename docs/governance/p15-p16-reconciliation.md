# P15-P16 Requirements and Traceability Reconciliation

## Baseline

- P15 completed through PR #58 at merge commit `5d3e7966a53668c9f38a3ad9feaf0a953afe8e14`.
- P16 starts from that merged baseline and is study-only.

## P16 requirements

| Requirement | Outcome | Evidence |
|---|---|---|
| REQ-0268 | Identify protected assets, trust boundaries, threats, abuse cases, and residual risk. | `docs/milestones/p16/threat-model.md` |
| REQ-0269 | Define mandatory authorization, limits, reconciliation, credential, kill-switch, audit, testing, and incident controls. | `docs/milestones/p16/control-matrix.md` |
| REQ-0270 | Assess legal, tax, custody, contractual, jurisdictional, and accountability questions without claiming legal conclusions. | `docs/milestones/p16/legal-accountability-review.md` |
| REQ-0271 | Produce an explicit go/no-go decision. | `docs/decisions/ADR-0044-live-order-execution-readiness-decision.md` |
| REQ-0272 | Keep live adapters, credentials, order submission, autonomous execution, and capital pilots out of scope. | ADR-0044 and P16 specification |
| REQ-0273 | Define objective reconsideration preconditions and a superseding-ADR rule. | Control matrix and ADR-0044 |
| REQ-0274 | Retain specification, OpenSpec, traceability, source review, exit evidence, and hosted Quality. | P16 milestone documentation and final PR evidence |

## Decision

P16 concludes **NO-GO** for real-money order execution. P17 remains unauthorized. No code path, credential, adapter, order endpoint, or pilot is introduced.

## External reference basis

The study uses current official guidance as risk input rather than as a claim that OSCA or its operator is a regulated firm. FINRA emphasizes holistic risk assessment, independent testing, post-deployment monitoring, controls, alerts, and reconciliation for algorithmic trading systems. NIST CSF 2.0 and SP 800-61 Rev. 3 provide governance and incident-response risk-management structures. Exact legal applicability requires qualified review for the intended jurisdiction and account.

## Preserved boundaries

P16 does not change provider admission, production ingestion, personal-server exposure, extension trust, recommendation boundaries, broker connectivity, autonomous execution, or real-capital authorization.
