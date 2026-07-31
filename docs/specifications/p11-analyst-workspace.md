# P11 Read-Only Analyst Workspace Specification

## Purpose

Provide one approachable local surface for inspecting retained OSCA datasets and evidence without reading raw SQLite tables or manually navigating artifact paths.

## Phase

Useful analyst workflow.

## User-visible value

Users can open a local browser workspace or JSON API and inspect projects, watchlists, governed datasets, research reports, backtest/paper evidence, SEC enrichment, and P10 routing decisions with visible status and provenance.

## Requirements

- REQ-0233: expose immutable workspace snapshot, section, and item contracts.
- REQ-0234: discover governed local OHLCV metadata and retained research/backtest artifacts.
- REQ-0235: discover retained SEC enrichment and runtime-routing evidence without initiating provider activity.
- REQ-0236: preserve blocked, unavailable, warning, stale, and available states rather than flattening them.
- REQ-0237: provide local JSON API and browser UI with loading, empty, warning, and error states.
- REQ-0238: remain read-only, loopback-bound by default, and free of credential-like metadata exposure.
- REQ-0239: retain tests, manual usage, OpenSpec, traceability, exit review, and hosted Quality evidence.

## Implementation scope

- Add `osca.analyst_workspace` contracts, discovery service, FastAPI app, and module CLI.
- Read P6 SQLite dataset metadata and retained local report files.
- Read P9 SEC evidence metadata and P10 routing-decision files where present.
- Support optional local project/watchlist JSON summaries without creating or mutating them.
- Expose `/health`, `/api/workspace`, and `/api/workspace/{section}`.
- Serve a minimal responsive page at `/` using the API and safe DOM text insertion.
- Provide `--snapshot` JSON output and loopback-only server binding.

## Explicit non-scope

- Artifact creation, editing, deletion, import, backtest execution, or provider requests.
- Full BI/dashboard authoring, chart builder, multi-user SaaS, authentication service, or extension marketplace UI.
- Remote/public binding, production hosting, provider credentials, recommendations, brokers, autonomous execution, or real-capital orders.

## Acceptance criteria

- Empty storage renders all governed sections with actionable empty messages.
- Existing local datasets, reports, backtests, SEC evidence, and routing decisions appear with stable item identity and provenance.
- P10 `policy_blocked` and `provider_unavailable` outcomes remain visible.
- Credential-like keys are omitted from surfaced metadata.
- Unsupported writes return method-not-allowed and the CLI refuses non-loopback hosts.
- Automated tests cover discovery, empty/error behavior, API/UI, status preservation, snapshot CLI, and binding controls.
- Manual testing, traceability, OpenSpec, exit evidence, and hosted Quality are current before P11 is marked complete.

## Dependencies

P6 local storage, P7 reports, P8 backtest/paper evidence, P9 enrichment evidence, and P10 routing provenance.

## Risks and decisions

- P11 intentionally uses server-rendered static HTML plus a small JSON API to avoid a frontend build-system dependency.
- The workspace displays retained evidence; it does not reinterpret evidence as advice.
- Missing project/watchlist artifacts produce honest empty states rather than synthetic examples.
- Any future write capability requires a separate governed milestone and explicit authorization model.
