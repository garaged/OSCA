# U10 — Research-Evidence Workspace

- **Status:** Complete and merge-ready
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

## Validation

Quality run #697 passed:

- Ruff;
- strict mypy across 242 source files;
- all 404 tests plus contract, migration, document-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

The [U10 clean-profile manual acceptance](manual-acceptance.md) also passed. The final retained chain used pipeline run `8423afa7-f95f-4e8e-a9e0-041824238b50`, experiment `d7552f55-93d9-4ec9-9b9a-dc1f1ac16fca`, versioned experiment and diagnostic contracts, complete upstream/downstream lineage, and a provider-policy-governed portable export. See the [U10 exit review](exit-review.md).

## Next milestone

U11 provides one canonical first-run and unified operator path through the primary `osca` CLI while preserving all U9/U10 provider, provenance, read-only, recommendation-disabled, and execution-disabled boundaries.

## Non-goals

U10 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote write APIs, or public evidence sharing.
