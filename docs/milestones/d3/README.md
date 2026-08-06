# D3 Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Validation reconciliation; macOS ARM64 and Linux x86-64 manual acceptance passed
- **Baseline:** D2 merge `7522da7bc50fa1fdffa4088c0f39f5d2ebe7d9b6`
- **Branch:** `agent/d3-provider-onboarding`
- **Pull request:** #83
- **Intent:** `intent.md`
- **Specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d3.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Validation evidence:** `validation-evidence.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d3-data-sources-acquisition/`

## Outcome

D3 turns the D2 offline shell into an honest data-source workspace. Users can inspect provider policy, manage named credentials through the OS vault, import governed local OHLCV evidence, explicitly run approved Kraken public acquisition, and inspect retained jobs and lineage without granting React or Rust provider, keychain, filesystem, database, or HTTP authority.

## Accepted architecture

- Python remains authoritative for policy, credentials, import, acquisition, evidence, and safety.
- Provider admission comes from `osca.production_ingestion.policy`.
- Credentials use `SecretVault`; desktop production composition uses `KeyringVault`.
- Credential values never return to React and never enter profile/analytical storage or ordinary logs.
- A stored credential does not promote a provider.
- Kraken public spot OHLC is the only D3 provider acquisition path.
- Governed CSV import and bundled synthetic sample remain universal no-cost offline paths.
- Network consent is explicit per acquisition request and disabled by default.
- The existing `desktop_request` Rust command remains the sole frontend bridge.
- Recommendations and all execution capabilities remain unavailable.

## Delivery slices

1. Specification, requirements, OpenSpec, traceability, and manual acceptance.
2. Provider catalog and capability resolution.
3. Secure credential lifecycle.
4. Governed local import desktop flow.
5. Kraken acquisition and job/evidence application methods.
6. Responsive accessible Data Sources UI.
7. Automated, hosted, and supported-platform manual validation.
8. Exit review and explicit owner-directed merge.

## Validation disposition

The repository owner reported the full D3 manual-acceptance procedure passed on macOS ARM64 and Linux x86-64. Defects found during acceptance were fixed on the D3 branch and covered by regression checks. Final D3 exit remains gated on refreshed hosted validation and explicit owner direction before merge.

## Known non-goals

D3 does not automatically promote providers, depend on a paid service, enable production acquisition for providers lacking accepted rights evidence, display secret values, add generic native capabilities, provide charting, create recommendations, or introduce broker/exchange/live-order behavior.
