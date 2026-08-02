# U10 — Research-Evidence Workspace

- **Status:** Implementation and automated conformance complete; clean-profile manual evidence pending
- **Baseline:** U9 merged through PR #72 at `80822eea84094d34123e2eaa6aa28cb9b7c7d2d9`
- **Branch:** `agent/u10-research-evidence-workspace`
- **Implementation PR:** #73

## Intent

Make the analyst workspace represent the complete retained research workflow instead of exposing model artifacts as generic reports.

## Delivered outcome

A retained U9/U8 workflow is navigable from dataset acquisition through experiment, diagnostic, optional validation, and pipeline-run evidence. Every view remains read-only and preserves provider, licensing, recommendation, promotion, broker, autonomous-execution, and real-capital boundaries.

Delivered capabilities:

1. Dedicated workspace sections for acquisitions, experiments, diagnostics, validations, and pipeline runs.
2. Read-only item detail contracts and endpoints with raw evidence, assumptions, warnings, and safety states.
3. Upstream/downstream lineage resolution using artifact-owned identities rather than mere references.
4. Explicit incomplete, corrupt, incompatible, and orphaned states.
5. Date, symbol, timeframe, type, and status filtering.
6. Bounded raw JSON download and portable evidence-bundle export consistent with provider policy.
7. HTML evidence navigation and shared CLI/API contracts.
8. CLI/API/export equivalence regression coverage.

## Automated validation

Quality run #692 passed:

- Ruff;
- strict mypy across 242 source files;
- all 404 tests plus contract, migration, document-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

## Remaining acceptance gate

Run [U10 clean-profile manual acceptance](manual-acceptance.md) using the retained U9/U8 evidence root and record the results in the [U10 exit review](exit-review.md).

The retained evidence must confirm:

- dedicated sections do not duplicate artifacts under generic reports;
- the U9 dataset, acquisition, U8 manifest, experiment, and diagnostic form one navigable lineage;
- validation is shown only when present and is explicitly not expected for diagnostic-ineligible runs;
- CLI and API identifiers and statuses agree;
- provider-restricted acquisition evidence is excluded from portable export;
- secrets and credentials are excluded;
- workspace remains loopback-only, read-only, network-disabled, recommendation-disabled, broker-disabled, and real-capital-disabled.

## Non-goals

U10 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote write APIs, or public evidence sharing.
