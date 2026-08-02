# U10 Exit Review

- **Milestone:** U10 research-evidence workspace
- **Status:** Complete and merge-ready
- **Implementation PR:** #73
- **Decision gate:** satisfied by clean-profile detail/filter/export evidence

## Delivered outcome

U10 upgrades the loopback-only analyst workspace from generic report discovery to a navigable retained research workflow.

Delivered capabilities:

- dedicated datasets, acquisitions, backtests, experiments, diagnostics, validations, and pipeline-run sections;
- no duplication of dedicated research evidence under generic reports;
- explicit available, review-required, not-eligible, incomplete, corrupt, incompatible, orphaned, policy-blocked, and provider-unavailable states;
- shared read-only detail contracts across CLI and API;
- upstream/downstream lineage using retained dataset, acquisition, experiment, diagnostic, validation, run, request, correlation, job, and URI identities;
- date, symbol, timeframe, type, and status filtering;
- bounded local JSON download with storage-root containment checks;
- policy-governed portable ZIP export with included/excluded item identifiers;
- exclusion of acquisition evidence when redistribution is disabled;
- secret and credential-field exclusion;
- HTML navigation into dedicated details;
- CLI/API/export equivalence regression coverage;
- preserved loopback-only, read-only, network-disabled, recommendation-disabled, promotion-disabled, broker-disabled, autonomous-disabled, and real-capital-disabled boundaries.

## Automated acceptance

Focused U10 tests cover:

- dedicated section classification and duplicate prevention;
- corrupt JSON handling;
- incomplete, incompatible, and orphaned state derivation;
- distinction between artifact-owned lineage identities and mere references;
- detail and lineage resolution;
- symbol/timeframe/type/status filtering and date-capable contracts;
- raw JSON endpoint behavior;
- portable export manifest contents and provider-policy exclusion;
- CLI/API/export identifier and count agreement;
- read-only safety boundaries.

Legacy P11 workspace coverage was reconciled to the U10 section model rather than retaining outdated generic-report expectations.

Quality run #697 passed on the final producer-contract head:

- Ruff;
- strict mypy across 242 source files;
- all 404 tests plus contract, migration, document-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

## Clean-profile manual acceptance

The final clean-profile run used the retained U9 dataset revision `dee68bf2-e8e1-5521-9e93-d2d6dc606bae` and regenerated the U8 research chain after the versioned experiment and diagnostic contract fix.

Retained identifiers:

- pipeline run: `8423afa7-f95f-4e8e-a9e0-041824238b50`;
- experiment: `d7552f55-93d9-4ec9-9b9a-dc1f1ac16fca`;
- experiment family/version: `osca.ml-experiment.result` / `1.0.0`;
- diagnostic family/version: `osca.prediction-diagnostic.result` / `1.0.0`;
- experiment status: `review_required`;
- diagnostic status: `review_required`;
- pipeline workspace status: `not_eligible` from retained `diagnostic_not_eligible` evidence.

The workspace snapshot contained six dedicated items and no warnings. The experiment detail resolved upstream links to the governed XBTUSD dataset and Kraken acquisition, and downstream links to the diagnostic and pipeline manifest. Raw JSON download and portable export were enabled only for the selected local evidence item.

The portable export included the experiment, diagnostic, and pipeline manifest. It excluded the Kraken acquisition because redistribution is disabled and excluded the Parquet dataset because the portable bundle is JSON-only. The export manifest retained all included and excluded item identifiers.

The workspace remained read-only. Network access, credential materialization, production ingestion, recommendations, broker connections, automatic promotion, autonomous execution, and real-capital orders remained disabled.

Validation evidence was correctly absent because the diagnostic did not qualify for U7 validation.

## Acceptance checklist

### Workspace organization

- [x] Dedicated research-evidence sections exist.
- [x] Dedicated artifacts do not duplicate under generic reports.
- [x] Malformed evidence is corrupt rather than healthy.
- [x] Missing required fields are incomplete.
- [x] Unsupported families or versions are incompatible.
- [x] Missing retained parents are orphaned.

### Navigation and filtering

- [x] Read-only artifact detail is available through CLI and API.
- [x] Upstream/downstream lineage is resolved from retained identities.
- [x] Date, symbol, timeframe, type, and status filter contracts exist.
- [x] HTML links expose dedicated evidence navigation.

### Download and export

- [x] Raw JSON download is bounded to the configured storage root.
- [x] Portable export contains a manifest with included and excluded identifiers.
- [x] Non-redistributable acquisition evidence is excluded.
- [x] Secret and credential fields are excluded.
- [x] CLI/API/export equivalence is covered automatically.

### Safety and quality

- [x] Workspace remains loopback-only and read-only.
- [x] Network retrieval and credential materialization remain disabled.
- [x] Recommendations, automatic promotion, brokers, autonomous execution, and real-capital orders remain disabled.
- [x] Final hosted Quality is green on the producer-contract head.
- [x] Clean-profile snapshot, detail, filter, and export evidence is retained.

## Residual limitations

- Lineage is resolved from retained explicit identifiers and URIs; artifacts that omit those fields are intentionally incomplete or orphaned rather than heuristically joined.
- Portable export includes eligible retained JSON evidence only. Parquet payloads, SQLite databases, raw provider payloads, and provider-restricted acquisition records are not silently redistributed.
- The workspace remains a local technical operator interface. U11 owns primary CLI startup, first-run diagnostics, and a unified beginner-facing workflow.

## Exit decision

U10 is complete and merge-ready. The implementation, hosted validation, clean-profile workspace navigation, lineage, filtering, governed export, provider-policy exclusion, and safety-boundary acceptance gates all passed.
