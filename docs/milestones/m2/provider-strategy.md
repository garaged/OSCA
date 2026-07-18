# M2 Reference-Provider Strategy

- **Status:** Accepted staged strategy; M2.7 candidates conditional on provider-specific licensing and conformance evidence
- **Governing roles:** Product, architecture, security, data, licensing, and quality authorities
- **Accepted:** 2026-07-18
- **Requirements:** REQ-0025–REQ-0029
- **Risks:** RISK-M2-002, RISK-M2-003, RISK-M2-004, RISK-M2-006, RISK-M2-007, RISK-M2-010

## Decision

M2.2 is provider-neutral and synthetic-fixture-first. It will accept one common provider capability/request/result/failure contract and prove it with deterministic stock and spot-crypto fixture adapters. Required CI evidence has no live network dependency and contains no provider credentials or provider-derived fixture whose redistribution rights are uncertain.

Twelve Data is the conditional M2.7 stock candidate. Kraken Spot is the conditional M2.7 cryptocurrency candidate. Candidate naming does not approve production visibility, retention, redistribution, backup, or fixture use.

## One-contract rule

Both candidates must implement the same public contract and pass the same conformance suite. Provider-specific behavior is expressed as machine-readable capability and policy metadata, not by changing canonical instrument, daily-bar, request, resolution, quality, or failure semantics.

The common profile covers:

- supported asset classes, venues, daily interval/history, completion and timestamp semantics;
- adjustment behavior and explicit absence of adjusted-bar support in M2;
- authentication and named credential references;
- fixed endpoint allowlists, timeouts, response/decompression limits, and safe parsing;
- quota units, observed limits, bounded retry categories, and backoff;
- acquisition, retention, transformation, export, backup, redistribution, and fixture rights;
- mapping/discovery identifiers and ambiguity behavior;
- typed authentication, policy, quota, transport, schema, mapping, quality, and compatibility failures;
- deterministic recorded or synthetic conformance fixtures.

## Promotion gates

A candidate becomes production-visible only when all applicable evidence is accepted:

1. official API documentation proves daily OHLCV coverage and required semantics;
2. the applicable account/plan and jurisdiction terms are identified;
3. licensing authority records operation-specific rights, restrictions, attribution, retention/deletion, and terms-review triggers;
4. security authority accepts endpoint, credential, input-bound, redaction, and resource-limit controls;
5. quota, retry, timeout, and health profiles are machine represented and failure tested;
6. the adapter passes the provider-neutral conformance suite without live-network CI;
7. any retained provider-derived fixture has explicit redistribution rights; otherwise synthetic fixtures prove conformance;
8. optional quarantined live checks do not become required release evidence;
9. provider transitions remain visible and cannot silently merge canonical series.

Failure or uncertainty at any gate keeps that candidate disabled and policy-blocked. It does not weaken M2.2 or establish a fallback provider.

## Current viability assessment

Twelve Data publicly documents market-data services and publishes terms that distinguish retention, deletion, non-display use, and redistribution. Those distinctions make an explicit plan/account rights review mandatory before OSCA retains or redistributes provider-derived material.

Kraken provides public Spot market-data APIs and downloadable historical trade data that can be transformed into other formats. The exact API/terms applicable to the operator's jurisdiction and the rights for retained normalized data and redistributed fixtures still require licensing review.

The pair is technically plausible for the stock and crypto stages, but neither candidate is approved merely by technical accessibility.

## Revisit triggers

Provider documentation, terms, plan, jurisdiction, endpoint, quota, response semantics, corporate ownership, or fixture provenance changes; conformance failure; inability to satisfy one-contract behavior; or discovery of mandatory paid/cloud coupling.
