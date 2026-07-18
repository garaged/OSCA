# M2 Risk Register

- **Status:** Proposed
- **Governing roles:** Product, security, data, licensing, architecture, and quality authorities
- **Review trigger:** Provider/policy/contract/persistence change, realized incident, or M2 exit
- **Last reviewed:** 2026-07-18

| ID | Risk | Criticality | Preventive/detective controls | Contingency | Owner | Review/trigger | Status |
|---|---|---|---|---|---|---|---|
| RISK-M2-001 | Ambiguous symbol mapping corrupts canonical identity | Critical | Provider-neutral IDs, time-aware verified mappings, ambiguity properties, quarantine | Block canonical write; correct mapping through new revision | Instrument owner | Every mapping/schema change | Open—treatment proposed |
| RISK-M2-002 | Provider terms prohibit retention/export/backup | Critical | Versioned policy metadata, rights review, fail-closed enforcement, fixture rights | Non-retention record; block operation; remove prohibited material through governed process | Licensing authority | Provider onboarding/terms change | Open—treatment proposed |
| RISK-M2-003 | Provider payload or parser silently corrupts bars | Critical | Immutable source evidence, checksums, bounded parser, golden fixtures, deterministic quality rules | Mark invalid, quarantine revision, targeted reingestion | Market Data owner | Adapter/parser change | Open—treatment proposed |
| RISK-M2-004 | Provider transition silently mixes series | Critical | One-source selection, visible provenance, no-merge property tests | Reject mixed revision; require later explicit reconciliation | Provider/Data owners | Routing/fallback change | Open—treatment proposed |
| RISK-M2-005 | Stale or partial data is represented as complete | High | Explicit request policy/resolution states, range/gap properties, health findings | Block strict caller; targeted repair | Market Data owner | Freshness policy change | Open—treatment proposed |
| RISK-M2-006 | Quota/rate exhaustion causes uncontrolled retry or cost | High | Central quota state, bounded retries/backoff, budgets, visible blocked state | Pause provider route; operator remediation/fallback | Provider owner | Adapter/quota change | Open—treatment proposed |
| RISK-M2-007 | Untrusted provider input causes SSRF, resource exhaustion, or disclosure | Critical | Fixed endpoint policy, named secrets, time/size/decompression/schema limits, redaction, adversarial fixtures | Fail closed; isolate adapter; security finding | Security/Provider owners | Adapter/network change | Open—treatment proposed |
| RISK-M2-008 | Cleanup removes protected or reproducibility-required data | Critical | Preview-first scopes, pin/protection, dependency checks, no automatic canonical deletion | Reject plan; restore metadata; re-fetch only when rights/availability permit | Cache/Catalog owners | Cleanup policy change | Open—treatment proposed |
| RISK-M2-009 | Payload persistence choice couples M2 to M3 engine needs | High | Separate metadata/payload ports, bounded daily requirements, ADR before selection | Replace adapter/migrate through contract; do not expand M2 | Architecture/Data owners | Persistence decision | Open—treatment proposed |
| RISK-M2-010 | Live-provider CI becomes flaky, secret-bearing, or irreproducible | High | License-safe immutable fixtures, adapter conformance, optional quarantined live checks | Block release claim; regenerate reviewed fixture | Quality/Provider owners | Fixture/provider change | Open—treatment proposed |

No critical risk may be accepted without rationale, residual impact, named owner, and review/expiry condition.
