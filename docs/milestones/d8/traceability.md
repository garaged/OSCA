# D8 Traceability — Virtual-Portfolio Accounting Foundation

| Authority / requirement | Planned implementation evidence |
|---|---|
| PRD §23.1-23.4; D-028 | `src/osca/paper/accounting.py`, append-only persistence, replay tests |
| ADR-0046 | Python accounting authority; typed desktop adapter; Rust ownership only |
| REQ-0375-0376 | portfolio lifecycle/store + starting-cash event tests |
| REQ-0377-0379 | journal contracts, Decimal arithmetic, balance/immutability tests |
| REQ-0380-0381 | replay/lot projection and explicit allocation tests |
| REQ-0382 | split/dividend/fork posting and idempotency tests |
| REQ-0383-0385 | valuation/projection/performance provenance tests |
| REQ-0386 | clone/reset lineage tests |
| REQ-0387-0388 | portable bundle export/restore tests |
| REQ-0389 | desktop API + Portfolio Lab frontend tests |
| REQ-0390 | offline/synthetic path and safety-boundary tests |
| REQ-0391-0392 | profile-lock/broker and migration/regression tests |
| REQ-0393 | semantic D8 module naming; architecture review |

This document records planned evidence while implementation is in progress. `validation-evidence.md` and `exit-review.md` must only claim completed gates after those gates have actually passed.
