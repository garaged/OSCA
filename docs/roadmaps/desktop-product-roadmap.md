# Desktop Product Roadmap

Status: Accepted

## Delivery sequence

| Milestone | Outcome | Primary dependencies |
|---|---|---|
| D1 | Desktop architecture and application API foundation | U14 baseline |
| D2 | Shell, design system, first-launch onboarding | D1 |
| D3 | Data-source, credential, import, and acquisition UX | D2 |
| D4 | Asset catalog, market browser, and watchlists | D3 |
| D5 | Production charting and quantitative-analysis workbench | D4 |
| D6 | Research projects, saved workspaces, and integrated evidence | D5 |
| D7 | Visual strategy builder and backtest lab | D5 |
| D8 | Virtual-portfolio accounting foundation | D7 |
| D9 | Forward paper evaluation and simulated orders | D8 |
| D10 | ML data platform, feature catalog, and experiment UX | D5, D6 |
| D11 | Model registry, validation, explainability, and drift | D10 |
| D12 | Recommendation engine and recommendation center | D7, D9, D11 |
| D13 | AI research assistant and natural-language evidence access | D6, D12 |
| D14 | Alerts, scheduling, and optional personal server | D3, D6, D9 |
| D15 | Reports, sharing, and governed export | D5, D6, D12 |
| D16 | Desktop extensions and developer experience | D1, D6 |
| D17 | Windows x86-64 support | D1-D16 relevant surfaces |
| D18 | Accessibility, localization, reliability, performance, and UX completion | D2-D17 |
| D19 | Desktop release-candidate and broadly usable release acceptance | D18 |

## Critical path

D1 → D2 → D3 → D4 → D5 → D7 → D8/D9 → D10/D11 → D12 → D18 → D19.

D6 follows D5. D13-D16 may progress in parallel where their dependencies and risk evidence allow. D17 must complete before D19.

## Milestone governance

Each milestone must include:

1. accepted intent and non-goals;
2. executable requirements and OpenSpec changes;
3. architecture and decision updates;
4. automated tests and hosted gates;
5. clean-profile manual acceptance;
6. migration, recovery, and known-limitation evidence where applicable;
7. requirements traceability and an exit review.

Milestones may be divided into coherent implementation slices, but their exit criteria cannot be weakened to fit implementation progress.

## Release invariants

- Offline import, sample data, cached data, deterministic analysis, and simulation remain usable without paid services.
- Provider-specific functionality remains capability-gated.
- Recommendations remain user-enabled research functionality and fail closed when evidence is incomplete.
- Local AI is user-managed initially; cloud AI is optional and user-credentialed.
- No milestone may introduce a live-order execution path.
