# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P15 governed analyst, ingestion, operations, and extension path:** Complete
- **Current activity:** P16 live-order readiness study
- **Live-order decision:** NO-GO through ADR-0044
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## P16 decision boundary

P16 evaluates whether OSCA may proceed toward real-money execution without implementing an order path.

- **Threat model:** capital, credentials, approvals, limits, venue ambiguity, replay, partial fills, reconciliation, emergency stops, audit, operations, and legal risk.
- **Control matrix:** every independent authorization, credential, limit, reconciliation, kill-switch, testing, release, incident, and accountability control is a mandatory blocker.
- **Decision:** current residual risk is unacceptable; real-money execution is NO-GO.
- **Reconsideration:** all blockers plus qualified external review and a superseding ADR are required.

## Preserved boundaries

No broker or exchange adapter, trading credential, order-intent surface, order submission, sandbox/production order, autonomous execution, or capital pilot is authorized. Research, paper evidence, schedules, and extension packs remain incapable of directly creating or submitting real orders.

## Authoritative navigation

- [P16 milestone](docs/milestones/p16/README.md)
- [P16 threat model](docs/milestones/p16/threat-model.md)
- [P16 control matrix](docs/milestones/p16/control-matrix.md)
- [ADR-0044](docs/decisions/ADR-0044-live-order-execution-readiness-decision.md)
- [P15-P16 reconciliation](docs/governance/p15-p16-reconciliation.md)
- [Architecture registry](engineering/architecture-registry.yaml)

## Validation state

P15 completed through PR #58 at merge commit `5d3e7966a53668c9f38a3ad9feaf0a953afe8e14`. P16 remains a study candidate until documentation, OpenSpec, traceability, hosted Quality, review, and merge are complete. Completion does not authorize P17.
