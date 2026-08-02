# Usable Release Roadmap: U9-U14

- **Status:** Approved implementation sequence
- **Baseline:** U8 merged through PR #69
- **Goal:** Reach a clean-machine, no-cost, evidence-complete OSCA release candidate without enabling recommendations, broker connectivity, autonomous execution, or real-capital orders.
- **Governing constraints:** ADR-0044 remains NO-GO; P17 remains blocked.

## Current position

OSCA has a functional local research engine, governed storage, deterministic analysis, backtesting, paper evidence, ML experiments, prediction diagnostics, human-gated model validation, a read-only workspace, personal-server operations, and trusted-local extensions.

The remaining path to a usable release is primarily product integration and release quality rather than additional analytical breadth.

## Sequence

| Milestone | Objective | Primary exit outcome |
|---|---|---|
| U9 | Governed no-cost historical-data acquisition | A clean install can acquire at least one equity and one Kraken crypto dataset without a paid account and normalize both through the canonical storage path. |
| U10 | Research-evidence workspace | The workspace displays complete dataset-to-validation lineage with dedicated experiment, diagnostic, validation, and pipeline-run views. |
| U11 | First-run and unified operator experience | A new user can initialize, diagnose, acquire/import data, run research, and start the workspace through the primary `osca` CLI. |
| U12 | Packaging, upgrade, backup, and rollback | Supported macOS and Linux clean installs, upgrades, failed-upgrade recovery, and rollback are evidenced. |
| U13 | Release-candidate acceptance | The official acceptance matrix passes and a release candidate is tagged. |
| U14 | Contributor and extension readiness | External contributors have stable contracts, templates, compatibility checks, and authoring documentation. |

## U9 — Governed no-cost historical-data acquisition

### Intent

Remove the external data-preparation dependency from the primary demonstration while preserving provider licensing, provenance, quality, and canonical revision controls.

### Scope

- Add a primary CLI acquisition surface, provisionally `osca historical-data fetch`.
- Support one no-cost equity acquisition path and the existing Kraken public-data path.
- Normalize all acquired observations through the existing governed OHLCV contracts and storage path.
- Retain provider capability, request, attribution, retrieval time, raw-response or non-retention evidence, parser/build identity, normalized digest, dataset revision, licensing policy, and quality findings.
- Preserve local CSV import as the provider-independent offline fallback.
- Fail closed for unsupported intervals, unavailable capabilities, licensing uncertainty, quota exhaustion, invalid credentials, malformed responses, and ambiguous instrument mappings.

### Governing requirements

REQ-0021, REQ-0023 through REQ-0038, REQ-0041, REQ-0042, and the universal evidence-based milestone exit gate.

### Exit gate

On a clean local profile, an operator can acquire AAPL daily history and one Kraken spot pair without a paid account, inspect retained lineage, and run the U8 research pipeline. Provider outage, quota, policy, and malformed-data scenarios produce actionable structured outcomes without corrupting accepted data.

## U10 — Research-evidence workspace

### Intent

Make the analyst workspace represent the complete retained research workflow instead of exposing model artifacts as generic reports.

### Scope

- Dedicated sections for datasets, backtests, experiments, diagnostics, validations, and pipeline runs.
- Read-only detail views with upstream/downstream lineage, evidence digests, safety states, warnings, assumptions, reviewer/rationale, and core metrics.
- Date, symbol, timeframe, type, and status filtering.
- Explicit incomplete, corrupt, incompatible, and orphaned evidence states.
- Raw JSON download and portable evidence-bundle export consistent with provider policy.
- Dynamic-port startup and CLI/API evidence-equivalence regression coverage.

### Exit gate

A completed U9/U8 run appears as one navigable lineage from acquired dataset through validation, and exported evidence agrees with CLI and API results.

## U11 — First-run and unified operator experience

### Intent

Let a technically capable new user complete the primary workflow without invoking internal modules or hand-authoring JSON.

### Scope

- Primary commands for `init`, `doctor`, workspace startup, acquisition/import, analysis, backtesting, experiments, diagnostics, and validation.
- Compatibility aliases for existing entry points during a documented deprecation window.
- Safe default local configuration.
- Structured corrective diagnostics and optional machine-readable output.
- Shell-safe quickstarts for zsh, Bash, and PowerShell.
- Diagnostics for runtime compatibility, writable storage, SQLite/Parquet readiness, ports, provider capability, credentials, and evidence consistency.

### Exit gate

A new user follows one canonical quickstart from installation to a populated workspace without manual JSON composition or `python -m osca.*` commands.

## U12 — Packaging, upgrade, backup, and rollback

### Intent

Create a repeatable supported installation and lifecycle experience.

### Scope

- Supported `uv tool` or equivalent isolated installation path.
- macOS Apple Silicon and Linux x86-64 validation.
- Versioning, changelog, checksums, SBOM, and provenance.
- Configuration/storage migration policy and compatibility checks.
- Backup-before-migration, failed-upgrade recovery, and rollback rehearsal.
- Packaged workspace startup and personal-server deployment guidance.

### Exit gate

Fresh install, workflow execution, upgrade, backup/restore, failed-upgrade recovery, and rollback pass on both supported platforms without loss of accepted evidence.

## U13 — Release-candidate acceptance

### Intent

Define and evidence the threshold for a usable release candidate.

### Acceptance matrix

1. Installation and initialization
2. No-cost historical acquisition
3. Local CSV fallback
4. Dataset quality, revision, and lineage
5. Deterministic analysis
6. Backtesting and paper evidence
7. ML experiment and diagnostics
8. Human-gated validation
9. Workspace browsing and evidence export
10. Backup and restore
11. Extension boundaries
12. Offline operation
13. Provider outage, quota, and policy behavior
14. Corrupt and incomplete artifact handling
15. Upgrade and rollback
16. Documentation/CLI agreement

### Exit gate

No critical or high-severity defects remain; primary workflows have one canonical command path; no paid provider is required for the principal demonstration; all results are traceable; safety boundaries remain disabled; and clean-machine acceptance passes before tagging the first release candidate.

## U14 — Contributor and extension readiness

### Intent

Make supported extension points usable by external contributors after the release candidate stabilizes the product surface.

### Scope

- Provider-adapter authoring guide and terms-evidence template.
- Trusted-local extension template and example external repository.
- Compatibility and conformance test kit.
- Public-contract stability and deprecation policy.
- Contributor quickstart, architecture boundaries, and review checklist.

### Exit gate

An external contributor can build and validate a provider adapter or trusted-local extension against documented stable contracts without modifying core application code.

## Explicit deferrals

The U9-U14 sequence does not authorize:

- investment recommendations;
- automated model promotion or live model serving;
- broker or exchange order connectivity;
- autonomous or real-capital execution;
- a controlled real-money pilot;
- an untrusted public extension marketplace;
- paid-provider dependency for the primary demonstration;
- new model families or indicator breadth unless required to close an acceptance defect.

## Delivery policy

- Use one coherent branch and PR per milestone by default.
- Keep `docs/testing/manual-testing.md` current in every operator-visible milestone.
- Each milestone follows Intent → Requirements → Architecture → Specification → Validation → Evidence.
- Hosted Ruff, strict mypy, pytest, OpenSpec, secret scanning, document-link checks, and architecture checks must pass before merge.
- Manual acceptance evidence is retained under the configured storage root when the milestone affects operator workflows.
