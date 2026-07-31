# P16 Live-Order Threat Model

## Decision context

This threat model evaluates whether the current single-user OSCA architecture can safely submit real-money orders. It does not authorize broker or exchange connectivity and does not provide legal advice.

## Protected assets

- Brokerage and exchange credentials, tokens, device approvals, and recovery material.
- Cash, securities, cryptoassets, margin capacity, and withdrawal authority.
- Order intent, approvals, limits, positions, executions, cancellations, and account statements.
- Market data, clocks, strategy versions, configuration, audit evidence, and incident records.
- Operator identity and the ability to stop all order activity independently of OSCA.

## Trust boundaries

1. Operator to OSCA approval surface.
2. OSCA research and strategy output to any future order-intent builder.
3. Order intent to a future broker/exchange adapter.
4. Adapter to external venue APIs and networks.
5. Venue acknowledgements, fills, balances, and statements back to OSCA.
6. Local host, extension packs, scheduler, backups, alerts, and secrets store.
7. Independent operator controls outside the OSCA process and host.

## Principal threats

| ID | Threat | Failure mode | Required mitigation before reconsideration |
|---|---|---|---|
| T-01 | Credential theft or misuse | Attacker or extension submits orders or withdraws assets. | Non-withdrawable trading credentials, hardware-backed storage, least privilege, rotation, revocation drills, independent account alerts. |
| T-02 | Unauthorized order generation | Bug, compromised host, or malicious input creates an order without valid human intent. | Two-step manual approval bound to an immutable order digest, short expiry, authenticated operator identity, no blanket approvals. |
| T-03 | Duplicate or replayed orders | Retry, crash, queue replay, or stale approval submits twice. | Durable idempotency keys, venue reconciliation, terminal-state tracking, replay rejection, restart testing. |
| T-04 | Stale or corrupt market/account data | Quantity or price is calculated from outdated balances, positions, or quotes. | Freshness gates, account snapshot versioning, independent venue query before submission, fail-closed clock and data checks. |
| T-05 | Limit bypass | Position, notional, leverage, loss, concentration, or frequency exceeds policy. | Pre-trade hard limits enforced outside strategy code, immutable limit profiles, independent tests, no runtime widening. |
| T-06 | Kill-switch failure | OSCA cannot cancel or prevent new orders during an incident. | Independent venue-side disablement, local deny switch, tested cancel-all workflow, documented authority and drills. |
| T-07 | Partial fill and reconciliation drift | Local state disagrees with venue state, causing accidental exposure. | Continuous order/fill/position/cash reconciliation, explicit unknown state, operator escalation, no new orders while unresolved. |
| T-08 | Venue/API ambiguity | Timeout leaves submission outcome unknown. | Query-by-client-order-id, unknown-state quarantine, no blind retry, venue-specific state machine evidence. |
| T-09 | Malicious or defective extension | Trusted-local pack influences order creation or accesses credentials. | Execution packs permanently excluded from order authority; separate signed, reviewed adapter boundary; no extension credential access. |
| T-10 | Host or supply-chain compromise | Modified dependency or binary changes order behavior. | Reproducible release provenance, signed artifacts, locked dependencies, isolated runtime, patch and vulnerability process. |
| T-11 | Audit loss or tampering | Order decisions cannot be reconstructed. | Append-only off-host evidence, synchronized time, signed digests, retention policy, account-statement comparison. |
| T-12 | Alerting or operator unavailability | Loss continues because alerts fail or nobody can intervene. | Independent venue alerts, escalation path, fail-safe limits, maximum unattended duration, operational coverage decision. |
| T-13 | Regulatory, tax, or contractual breach | Use violates jurisdiction, account agreement, reporting, or advisory obligations. | Written jurisdiction/account review by qualified counsel and tax professionals; explicit accountable owner. |
| T-14 | Model or strategy error | Valid software faithfully submits economically harmful orders. | Live execution cannot rely on model confidence; human approval, bounded pilot policy, independent risk review, loss limits. |

## Abuse cases

- A caller attempts to turn paper evidence directly into a live order.
- A scheduled job attempts to submit an order without a contemporaneous approval.
- An extension pack declares or infers broker permissions.
- A failed request is retried without knowing whether the venue accepted it.
- A configuration change widens limits while orders are active.
- Local position state is trusted after connectivity loss.
- A kill switch depends on the same process, host, credentials, or network path that failed.

All cases must remain impossible or fail closed in the current product.

## Current disposition

Current controls provide useful foundations for evidence, permissions, scheduling, alerts, recovery, and trusted-local extensions. They do not yet provide independent order authorization, venue reconciliation, credential custody, pre-trade hard limits, or independently tested emergency stop authority. Residual risk is therefore unacceptable for real-money execution.
