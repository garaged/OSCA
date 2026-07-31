# P16 Live-Order Readiness Study Specification

## Purpose

Produce a decision-quality threat model, mandatory control baseline, legal/accountability review, and go/no-go ADR without implementing real-money execution.

## Requirements

- **REQ-0268:** Identify protected assets, trust boundaries, principal threats, abuse cases, and residual risk for real-money order execution.
- **REQ-0269:** Define mandatory authorization, separation, credential, limit, idempotency, venue-state, reconciliation, kill-switch, monitoring, audit, testing, release, and incident controls.
- **REQ-0270:** Identify legal, tax, custody, contractual, jurisdictional, liability, and accountability questions requiring qualified external review.
- **REQ-0271:** Record an explicit go/no-go architecture decision supported by the study evidence.
- **REQ-0272:** Preserve a hard non-scope boundary around broker/exchange adapters, trading credentials, order submission, sandbox/production orders, autonomous execution, and real-capital pilots.
- **REQ-0273:** Define objective reconsideration preconditions and require a superseding ADR before later implementation.
- **REQ-0274:** Retain requirements, traceability, sources, milestone status, OpenSpec, exit review, and hosted Quality evidence.

## Decision

P16 concludes `NO-GO` for real-money order execution. Existing research, paper, scheduler, and extension capabilities must remain incapable of directly creating or submitting real orders.

## Acceptance criteria

- Threat and control evidence covers both technical and operational failure modes.
- Unresolved legal applicability is identified rather than guessed.
- ADR-0044 states the decision, consequences, prohibited shortcuts, and reconsideration rule.
- P17 remains explicitly unauthorized.
- No executable order path or credential material is added.
- Documentation links, traceability, OpenSpec strict validation, secret scanning, and hosted Quality pass.

## External evidence interpretation

Current official FINRA guidance is used as evidence that algorithmic trading risk programs emphasize holistic assessment, independent testing, production monitoring, controls, alerts, and reconciliation. NIST CSF 2.0 and SP 800-61 Rev. 3 are used as general cybersecurity governance and incident-response frameworks. These references do not establish that OSCA or its operator is subject to any particular rule; exact applicability requires qualified review.

## Dependencies

P13-P15 production ingestion, personal-server operations, and extension trust boundaries.
