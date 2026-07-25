# M7 Risk Register

| Risk | Description | Treatment |
|---|---|---|
| M7-R-001 | Event order or identity ambiguity corrupts simulation evidence. | Use typed event identities, timezone-aware effective time, and explicit lifecycle links. |
| M7-R-002 | Invalid order lifecycle transitions create impossible histories. | Validate lifecycle transitions before promotion to simulation evidence. |
| M7-R-003 | Fill approximations are mistaken for higher fidelity than F2 supports. | Require model metadata and keep tick/quote/order-book fidelity deferred. |
| M7-R-004 | Strategy or extension bypasses deterministic risk. | Represent risk outcomes as authoritative simulation gates. |
| M7-R-005 | Accounting imbalance hides portfolio errors. | Require journal transactions to balance by currency. |
| M7-R-006 | Multi-currency valuation loses source lineage. | Require price and FX source identity in valuation snapshots. |
| M7-R-007 | F2 approval accidentally activates forward paper behavior. | Promotion gates may approve evidence only; F3 activation remains deferred. |
