# P11 - Read-Only Analyst Workspace

- **Status:** Implementation candidate, review ready
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Provide a focused local browser/API workspace for inspecting retained OSCA datasets and evidence while preserving provenance and fail-closed states.
- **Baseline:** Completed M0-M12 roadmap and P1-P10
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality run `30643690550` passed on PR #54

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p11-analyst-workspace.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p11-analyst-workspace/spec.md)
- [Requirements and traceability reconciliation](../../governance/p10-p11-reconciliation.md)
- [User testing quickstart](user-testing-quickstart.md)
- [Exit review](exit-review.md)

## Objective

Turn the P6-P10 local evidence path into an approachable read-only product surface without introducing a frontend toolchain, mutation APIs, or provider activity.

## User-visible value

Users can inspect retained projects, watchlists, datasets, reports, backtests, SEC evidence, and routing outcomes from a local browser or JSON API. Empty sections are explicit, and policy blocks remain visible.

## Implemented scope

- Immutable workspace snapshot, section, item, and status contracts.
- P6 local dataset discovery from SQLite.
- Retained P7 research and P8 backtest/paper report discovery.
- P9 SEC metadata and P10 routing-decision discovery where retained.
- Optional local project/watchlist JSON summary discovery.
- Preserved `available`, `warning`, `policy_blocked`, and `provider_unavailable` states.
- `/`, `/health`, `/api/workspace`, and `/api/workspace/{section}`.
- `python -m osca.analyst_workspace --snapshot` and loopback-only server mode.
- Credential-like metadata key filtering before presentation.

## Explicit non-scope

- Creating, editing, deleting, importing, backtesting, or invoking providers.
- Full BI, chart authoring, multi-user SaaS, remote/public hosting, or marketplace UI.
- Provider credentials, recommendations, brokers, autonomous execution, or real-capital orders.

## Validation evidence

- Ruff passed.
- Strict mypy passed across 188 source files.
- 317 tests passed, including all eight P11 workspace tests.
- Contracts, migrations, links, and architecture checks passed.
- OpenSpec doctor and strict validation passed.
- Secret scanning passed.
- Quality run `30643690550` is the accepted assembled-implementation evidence.

## Acceptance criteria

- REQ-0233-REQ-0239 reflect the read-only workspace scope.
- Empty storage presents all sections with honest empty states.
- Existing artifacts are discoverable with provenance and stable status.
- P10 blocked/unavailable routing decisions remain unchanged in presentation.
- The API has no mutation endpoints and non-loopback startup fails closed.
- Manual usage, traceability, OpenSpec, exit evidence, and hosted Quality are current.

## Risks and decisions

- The interface is deliberately read-only and loopback-only.
- No project/watchlist records are synthesized when none exist.
- P11 displays evidence and routing rationale; it does not produce financial advice.
- Any future mutation or remote-access capability requires a separate governed milestone.
