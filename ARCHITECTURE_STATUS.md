# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0-M12 governed foundation roadmap:** Complete
- **P1-P5 provider governance and reconciliation:** Complete
- **P6-P8 usable no-cost local evidence workflow:** Complete
- **P9 SEC preview and FRED terms gate:** Complete through PR #52
- **P10 capability-based runtime routing:** Complete through PR #53
- **P11 read-only analyst workspace:** Complete through PR #54
- **Current optional activity:** P12 local model-assisted preview implementation candidate in PR #55
- **Freeze point:** Foundational ADR freeze remains in effect; semantic changes require governed supersession

## Authoritative navigation

- [Product requirements](docs/product-requirements.md)
- [Architecture decisions](docs/decisions/README.md)
- [P11-P12 reconciliation](docs/governance/p11-p12-reconciliation.md)
- [P12 milestone](docs/milestones/p12/README.md)
- [P12 user testing quickstart](docs/milestones/p12/user-testing-quickstart.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Remaining P roadmap](docs/milestones/remaining-p-roadmap.md)

## Usable deterministic analyst path

P6-P11 already provide a usable no-cost local workflow:

1. governed local CSV/Parquet OHLCV import
2. deterministic research observations
3. transparent backtest and linked local paper evidence
4. SEC fixture replay and optional bounded SEC preview
5. capability-based routing with blocked/unavailable/partial states
6. a loopback-only read-only analyst workspace

FRED and model providers are optional. Their absence does not block this path.

## P12 preview boundary

P12 adds `osca.model_preview` as an optional evidence-oriented surface:

- deterministic zero-cost ordinary-least-squares trend inference
- fixture-backed LLM analysis with exact provider/model/prompt identity
- input, output, cost, and latency budgets
- input digests, metrics, findings, review status, and atomic evidence retention
- explicit `succeeded`, `review_required`, `budget_exceeded`, `policy_blocked`, and `provider_unavailable` states

Network/model calls remain disabled by default. Missing fixtures are policy-blocked. Explicit live checks remain provider-unavailable until a separately governed executor exists. LLM fixture output is untrusted until human review and is never represented as financial advice.

## Deferred boundary

The following remain disabled:

- FRED live API access and retention
- paid/authenticated provider promotion without evidence
- remote model invocation or credential resolution
- production model serving or automated model promotion
- scheduled production ingestion or real-time streaming
- recommendations presented as authoritative advice
- broker or exchange connections
- autonomous strategy execution
- live or real-capital orders

## Validation state

P11 is complete with final Quality run `30643815365` and merge commit `cdd5c3d50c4166ae8f01be2bcee45eb5f411cbb7`. P12 remains an implementation candidate until PR #55 passes hosted Quality, review, and final evidence reconciliation.
