# U10 Exit Review

- **Milestone:** U10 research-evidence workspace
- **Status:** Completion candidate
- **Implementation PR:** #73
- **Decision gate:** final hosted Quality plus clean-profile detail/filter/export evidence

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
- detail and lineage resolution;
- symbol/timeframe/type/status filtering and date-capable contracts;
- raw JSON endpoint behavior;
- portable export manifest contents and provider-policy exclusion;
- CLI/API/export identifier and count agreement;
- read-only safety boundaries.

Legacy P11 workspace coverage was reconciled to the U10 section model rather than retaining outdated generic-report expectations.

## Clean-profile manual acceptance

Run `docs/milestones/u10/manual-acceptance.md` against `.osca/u9-acceptance` or another retained U9/U8 chain.

Retain:

- full workspace snapshot;
- filtered experiment output;
- one experiment detail output;
- portable ZIP manifest;
- selected item identifiers;
- applicable lineage links;
- any warnings and their interpretation;
- confirmation that non-redistributable acquisition evidence was excluded;
- confirmation that CLI and API identifiers/statuses agree;
- confirmation that recommendation and execution boundaries remain disabled.

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
- [ ] Final hosted Quality is green on the documentation-closeout head.
- [ ] Clean-profile snapshot, detail, filter, and export evidence is retained.

## Residual limitations

- Lineage is resolved from retained explicit identifiers and URIs; artifacts that omit those fields are intentionally incomplete or orphaned rather than heuristically joined.
- Portable export includes eligible retained JSON evidence only. Parquet payloads, SQLite databases, raw provider payloads, and provider-restricted acquisition records are not silently redistributed.
- The workspace remains a local technical operator interface. U11 owns primary CLI startup, first-run diagnostics, and a unified beginner-facing workflow.

## Exit decision

U10 implementation and automated conformance are completion candidates. Mark U10 complete only after the latest hosted Quality run passes and the clean-profile U9/U8 detail, filter, and portable-export evidence is retained and interpreted.
