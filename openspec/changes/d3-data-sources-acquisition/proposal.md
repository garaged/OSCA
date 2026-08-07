# Proposal: D3 Data Sources, Credentials, Import, and Acquisition UX

## Why

D2 provides a safe offline desktop shell but intentionally leaves provider setup, credential storage, local-file import, network acquisition, and acquisition evidence unavailable. The Python core already has provider admission policy, OS-vault abstractions, canonical local import, bounded production ingestion, and governed Kraken historical acquisition. D3 must expose those capabilities without duplicating authority or weakening free/offline and no-live-execution boundaries.

## What changes

- Add a Data Sources destination backed by canonical provider admission policy.
- Distinguish admission, credential, network, profile, resource, and operational status.
- Add named credential store/probe/delete through `SecretVault` and OS keyring, never returning secret values.
- Preserve sample and governed CSV import as credential-free offline paths.
- Add a canonical local OHLCV CSV import wizard.
- Add explicit request-scoped networking and approved Kraken public spot OHLC acquisition.
- Add typed acquisition progress, retained evidence, cancellation, retry, reuse, and recovery UX.
- Display provider licensing/promotion blockers without automatically changing policy.
- Preserve the narrow React → Rust `desktop_request` → Python boundary.
- Add security-redaction, network-negative, provider-policy, import, acquisition, frontend, accessibility, hosted, and manual validation.

## Non-goals

D3 does not automatically promote providers, require a paid provider, run Twelve Data or other evidence-blocked production acquisition, embed or reveal credentials, grant frontend/Rust generic native authority, redistribute provider data, add charting, generate recommendations, or create broker/exchange/live-order/real-capital behavior.

## Exit outcome

A user can understand every provider's governed status, use OS-backed named credentials safely, import local evidence offline, explicitly retrieve approved Kraken public OHLC, inspect retained provenance and job outcomes, cancel/retry/recover safely, and understand every unavailable state while credentials remain secret and Python remains authoritative.
