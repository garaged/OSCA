# P16 Legal and Accountability Review

## Purpose

Identify questions that must be resolved by qualified professionals and named accountable owners before OSCA can reconsider real-money execution. This document is not legal, tax, accounting, or investment advice.

## Required external review

The exact jurisdiction, operator residence, account owner, venue, asset class, account type, and intended users materially change the analysis. A future proposal must obtain written review covering:

- Whether the operator is acting only for their own account or for another person or entity.
- Whether software behavior could constitute investment-adviser, broker-dealer, commodity-trading, money-transmission, fiduciary, or similar regulated activity.
- Venue and brokerage account agreements governing APIs, automation, credential sharing, market data, order types, rate limits, and prohibited conduct.
- Market-manipulation, wash-trading, spoofing, layering, best-execution, supervision, recordkeeping, and reporting obligations applicable to the exact activity.
- Tax-lot, cost-basis, gains/losses, fee, staking, derivatives, foreign-account, and jurisdiction-specific reporting requirements.
- Custody, withdrawal, insolvency, counterparty, margin, lending, and asset-segregation risks.
- Privacy, cybersecurity, breach notification, evidence retention, and cross-border data-transfer duties.
- Liability allocation for software defects, venue outages, bad data, unauthorized activity, and missed cancellations.

## Accountable roles required

A single developer/operator cannot silently hold every authority. Before reconsideration, the proposal must name accountable owners for:

| Authority | Responsibility |
|---|---|
| Product owner | Defines exact pilot scope and capital ceiling. |
| Risk owner | Approves limits and can stop activity independently. |
| Security owner | Owns credentials, host security, incident response, and release provenance. |
| Compliance/legal reviewer | Confirms jurisdiction and account-contract acceptability. |
| Operations owner | Reconciles orders, fills, positions, cash, fees, and statements. |
| Incident commander | Has authority to stop, cancel, revoke, preserve evidence, and communicate. |

For a personal single-user deployment, one person may perform multiple roles, but the decisions and checks must remain explicit and independently reviewable. Self-approval alone is insufficient for high-impact control changes.

## Current conclusion

No written legal/account review, named execution-risk owner, independent security review, or operational coverage model exists in the repository. Therefore legal and accountability readiness is unresolved and blocks live-order implementation.
