# P16 Mandatory Live-Order Control Matrix

## Interpretation

Every control below is a prerequisite for reconsidering live-order implementation. `Required` does not mean implemented. P16 authorizes no order path.

| Control area | Mandatory control | Current state | Gate |
|---|---|---|---|
| Product authority | Explicit product approval for a named pilot, instruments, venue, jurisdiction, account, and maximum capital. | Missing | Blocker |
| Legal/account | Written review of account agreement, jurisdiction, advisory status, market rules, tax/reporting, liability, and data retention. | Missing | Blocker |
| Human approval | Per-order authenticated approval bound to symbol, side, type, quantity, limit, account, expiry, and digest. | Missing | Blocker |
| Separation | Research/model output cannot directly submit; order construction, risk approval, and transport are distinct authorities. | Missing | Blocker |
| Credentials | Trading-only, non-withdrawable credentials; hardware-backed or external secret custody; rotation and emergency revocation tested. | Missing | Blocker |
| Pre-trade limits | Independent hard caps for notional, quantity, position, concentration, leverage, price deviation, order rate, daily loss, and open orders. | Missing | Blocker |
| Limit governance | Limits cannot be widened by strategies, extensions, or an active order session; changes require separate approval and audit. | Missing | Blocker |
| Idempotency | Durable client order IDs, replay rejection, and restart-safe submission state. | Missing | Blocker |
| Venue state | Explicit state machine for submitted, acknowledged, partially filled, filled, cancelled, rejected, expired, and unknown. | Missing | Blocker |
| Reconciliation | Continuous comparison of orders, fills, positions, cash, fees, and statements; drift blocks new orders. | Missing | Blocker |
| Kill switches | Local deny-new-orders, venue-side disablement, cancel-all, credential revocation, and account lock procedures. | Missing | Blocker |
| Independence | At least one stop mechanism works outside the OSCA process and host. | Missing | Blocker |
| Monitoring | Independent venue alerts plus OSCA alerts for submissions, fills, rejects, unknown states, limit events, and reconciliation drift. | Partial | Blocker |
| Audit | Append-only, off-host evidence with synchronized timestamps, digests, approvals, request/response lineage, and redaction. | Partial | Blocker |
| Testing | Venue sandbox tests, fault injection, duplicate/replay tests, timeout ambiguity, partial fills, crash recovery, and kill-switch drills. | Missing | Blocker |
| Release | Signed release, reviewed diff, locked dependencies, provenance, rollback plan, and isolated deployment identity. | Partial | Blocker |
| Incident response | Named authority, severity model, stop/cancel/revoke/reconcile procedures, evidence preservation, and post-incident review. | Partial | Blocker |
| Operational coverage | Maximum unattended duration, operator availability, alert escalation, maintenance windows, and venue outage policy. | Missing | Blocker |
| Pilot limits | Cash-only or otherwise explicitly approved account; no withdrawals, margin, shorting, derivatives, or leverage by default. | Not authorized | Blocker |
| Exit criteria | Defined pilot success/failure thresholds and automatic reversion to no-go after any control breach. | Missing | Blocker |

## Minimum reconsideration evidence

A future proposal must include:

1. Qualified legal and account-contract sign-off for the exact operating context.
2. An accepted superseding ADR naming accountable owners.
3. A broker/exchange adapter specification with no shared extension runtime authority.
4. Independent security review and threat-model closure.
5. Test evidence for all failure states and emergency controls.
6. Paper and sandbox observation periods with zero unresolved reconciliation drift.
7. A tiny, fixed-capital pilot proposal that remains manually approved per order.

Missing any item means `NO-GO`.
