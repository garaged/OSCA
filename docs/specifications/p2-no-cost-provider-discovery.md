# P2 No-Cost Provider Discovery Specification

- **Status:** Accepted
- **Milestone:** P2
- **Requirements:** REQ-0168 through REQ-0176
- **ADR:** ADR-0040
- **Last updated:** 2026-07-25

## Intent

P2 defines the governed discovery baseline for no-cost provider candidates so OSCA can preserve a no-spend operating path while avoiding legally ambiguous or operationally brittle integrations.

## Scope

P2 includes provider candidate classification, official-source evidence notes, cost/account/key classification, capability fit, licensing and quota uncertainty, exclusion policy, implementation sequencing guidance, and retained governance evidence.

P2 does not implement adapters, provider API calls, credential materialization, production ingestion jobs, runtime provider routing, production promotion decisions, external redistribution/export behavior, live execution, or real-capital orders.

## Acceptance Criteria

| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| P2-AC-001 | REQ-0168, REQ-0169 | A discovery catalog records each provider candidate or exclusion with source notes and uncertainty disposition. | Inspection |
| P2-AC-002 | REQ-0170, REQ-0171 | Provider entries classify cost model, account/key requirement, payment requirement, and capability fit. | Inspection |
| P2-AC-003 | REQ-0172 | Unclear licensing, redistribution, automation, or account-plan evidence fails closed. | Inspection |
| P2-AC-004 | REQ-0173 | Known quota, rate-limit, fair-access, and user-agent constraints are retained. | Inspection |
| P2-AC-005 | REQ-0174 | The catalog records implementation sequencing recommendations for future governed work. | Inspection |
| P2-AC-006 | REQ-0175 | P2 retains an explicit no-implementation/no-promotion boundary. | Inspection |
| P2-AC-007 | REQ-0176 | Traceability, manual testing, ADR, OpenSpec, and hosted Quality evidence are retained. | Hosted Quality and inspection |

## Candidate Dispositions

P2 recognizes preferred candidate, conditional candidate, research-only, and excluded dispositions.

Preferred and conditional candidates are not production approved. They only become eligible for implementation or promotion when a later governed milestone accepts fresh evidence under P1 controls.
