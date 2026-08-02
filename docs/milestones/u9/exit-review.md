# U9 Exit Review

- **Milestone:** U9 governed no-cost historical data acquisition
- **Status:** Complete and merge-ready
- **Implementation PR:** #72
- **Decision:** All implementation, hosted validation, governance, and clean-profile acceptance gates pass

## Delivered outcome

U9 provides a first-class governed historical-acquisition path through the primary `osca` CLI. Kraken public spot OHLC is admitted for internal research use. No no-cost equity provider is admitted without sufficient display, retention, export, backup, and redistribution evidence; equity acquisition therefore fails closed and directs the operator to governed CSV import.

The final U9 contract includes:

- timezone-aware bounded start/end ranges and half-open range filtering;
- venue context and verified provider pair mapping;
- freshness, completeness, and minimum-row expectations;
- persisted request, correlation, job, and acquisition identities;
- progress, attempts, duration, reuse, cancellation, and interrupted-job recovery;
- explicit fresh, stale, partial, invalid, corrupt, refreshing, quota-blocked, credential-blocked, policy-blocked, unavailable, cancelled, failed, and succeeded states;
- raw and normalized SHA-256 evidence;
- parser and normalizer identities;
- immutable processing-aware revisions and predecessor/supersession lineage;
- provider attribution, quota/retry data, findings, and remediation;
- U8 pipeline compatibility;
- recursive read-only workspace discovery of the complete existing evidence chain;
- disabled recommendations, promotion, brokers, autonomous execution, and real-capital orders.

## Provider disposition

| Provider | U9 status | Rationale |
|---|---|---|
| Kraken public spot OHLC | admitted | Public no-key endpoint, internal use, bounded retention, attribution, and no redistribution |
| Twelve Data | needs evidence / policy blocked | Free material does not establish OSCA's full display, retention, export, backup, and redistribution boundary |
| Alpha Vantage | needs evidence | Exact account-plan and intended-use evidence remains insufficient |
| Nasdaq Data Link | needs evidence | Rights remain dataset and order-form specific |
| FRED | policy blocked | Existing retention and software/AI-use concerns remain unresolved |

## Retained real-world evidence

### Kraken acquisition

The August 2, 2026 clean-profile run succeeded for XBTUSD 1d:

- 720 canonical rows;
- dataset revision `dee68bf2-e8e1-5521-9e93-d2d6dc606bae`;
- raw digest `sha256:13a8a05f68560ef535562d422414e3a04182d90b351dd781ae669e6dab44c71b`;
- parser `kraken-ohlc-v1`;
- current uncommitted bar excluded;
- redistribution, recommendations, broker execution, and real-capital execution disabled.

This retained run predates the additive v2 acquisition contract. The final v2 identity, lifecycle, status, mapping, range, normalized-digest, and correction-lineage fields are validated by the hosted deterministic suite.

### U8 research handoff

The exact acquired payload and revision were accepted by U8 run `d2cfcf58-ce0d-4bf9-be04-62ed84abb61d`, experiment `7de528ca-64d8-4dd8-be44-8458a28c6c50`. The diagnostic returned `review_required`, so the pipeline correctly stopped with `diagnostic_not_eligible` and retained the manifest, experiment, and diagnostic without creating validation evidence.

### Blocked equity

The clean-profile Twelve Data request produced no provider payload or canonical revision and retained CSV fallback guidance with every recommendation and execution boundary disabled. The final v2 taxonomy represents this as `policy_blocked`; the earlier retained output used the predecessor `provider_unavailable` label.

### Workspace discovery

A clean-profile workspace snapshot was generated at `2026-08-02T14:57:28.095141Z` from `.osca/u9-acceptance`.

The snapshot retained eight discoverable items:

- dataset revision `dee68bf2-e8e1-5521-9e93-d2d6dc606bae`, with 720 XBTUSD 1d bars from `2024-08-12T00:00:00+00:00` through `2026-08-01T00:00:00+00:00`;
- Kraken historical-acquisition evidence;
- blocked Twelve Data equity evidence;
- raw Kraken production-ingestion payload;
- Kraken production-ingestion metadata;
- U8 experiment artifact;
- U8 diagnostic artifact;
- U8 pipeline manifest.

The snapshot reported no warnings. It also confirmed:

- `read_only: true`;
- `network_access_enabled: false`;
- `credential_materialization_enabled: false`;
- `production_ingestion_enabled: false`;
- `recommendations_enabled: false`;
- `broker_connections_enabled: false`;
- `real_capital_orders_enabled: false`.

Validation artifacts were correctly absent because the diagnostic was not eligible for U7 validation. Persisted v2 acquisition-job evidence is covered by the focused automated workspace-chain regression; the retained clean-profile evidence originated before the additive v2 contract and therefore does not contain that later artifact.

## Acceptance checklist

### Product and contract

- [x] Canonical bounded start/end range and timezone validation.
- [x] Venue context and verified provider pair mapping.
- [x] Freshness, completeness, and minimum-row expectations.
- [x] Persisted request, correlation, acquisition, and job identities.
- [x] Progress, attempts, duration, reuse, cancellation, and restart recovery.
- [x] Full degraded-outcome taxonomy with remediation and retry data.
- [x] Raw and normalized digests.
- [x] Parser/normalizer revision identity and predecessor/supersession lineage.
- [x] CSV and network acquisition canonical compatibility.
- [x] U8 pipeline consumes the acquired payload and revision.
- [x] Blocked equity is explicit, non-networked, and preserves CSV fallback.
- [x] Recommendation, promotion, broker, and real-capital boundaries remain false.

### Workspace evidence chain

- [x] Automated regression proves the workspace discovers the canonical dataset.
- [x] Automated regression proves discovery of historical-acquisition evidence.
- [x] Automated regression proves discovery of persisted acquisition-job evidence.
- [x] Automated regression proves discovery of the U8 manifest, experiment, and diagnostic.
- [x] Validation evidence is required only when diagnostic eligibility permits U7.
- [x] Workspace remains read-only with network and execution capabilities disabled.
- [x] Final clean-profile `--snapshot` output is retained and contains the complete applicable real evidence chain.

### Quality and governance

- [x] Ruff passes on the strict configuration.
- [x] Strict mypy passes across 240 source files.
- [x] Latest full pytest/contracts/migrations/links/architecture run is green.
- [x] OpenSpec doctor and strict validation pass.
- [x] Secret scan passes.
- [x] Manual testing guide covers happy path, ranges, lifecycle, failures, U8 handoff, and workspace discovery.
- [x] Requirement-to-implementation/test/evidence traceability is retained.
- [x] `.osca/` is ignored by Git.

## Exit decision

U9 is complete and ready to merge. The admitted Kraken path, blocked-equity fallback, canonical revisioning, durable lifecycle, degraded-state taxonomy, lineage, U8 handoff, complete applicable workspace discovery, governance documentation, and safety boundaries all pass. Hosted Quality run #668 passed on the pre-closeout implementation head; the final closeout commit changes documentation only and must retain the same green checks.

Dedicated acquisition, experiment, diagnostic, and validation workspace sections and detail pages remain U10 scope. U10 must not weaken the provider, licensing, provenance, read-only, or execution boundaries established by U9.
