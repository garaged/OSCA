# Desktop Capability Map

Status: Active implementation authority through D10

Legend: **current** exists in the retained Python/U14 product; **foundation** is implemented as reusable desktop infrastructure; **planned** belongs to a future milestone; **gated** requires separate evidence or user enablement; **prohibited** must not be implemented.

| Capability | State | Milestone or gate |
|---|---|---|
| Local file import, sample data, cached research | current | Preserve throughout |
| Deterministic bundled synthetic desktop sample | foundation | D2; offline, provider-free, credential-free |
| Kraken public historical crypto OHLC | current/gated | Existing provider governance |
| Additional market, fundamentals, news, estimates, options, and alternative-data providers | gated | D3 plus provider-promotion evidence |
| Browser evidence workspace and CLI | current | Preserve while desktop matures |
| Versioned desktop application API and sidecar broker | foundation | D1 |
| Responsive desktop shell and primary navigation | foundation | D2 |
| Desktop onboarding and permanent safety disclosures | foundation | D2 |
| Desktop profile list, inspect, create, select, and open | foundation | D2; Python-authoritative |
| Desktop system diagnostics and explicit failure states | foundation | D2 |
| Desktop accessibility and semantic design-system foundation | foundation | D2; completed release-wide in D18 |
| Native profile-directory chooser | planned | Narrow host capability after D2 evidence; no generic frontend filesystem access |
| Provider and credential setup UX | planned/gated | D3; provider and credential policy evidence |
| Asset discovery and watchlists | foundation | D4 |
| Interactive charts and quantitative workbench | foundation | D5 |
| Research projects and saved workspaces | current | D6 |
| Strategy builder and backtesting lab | current | D7 |
| Multiple virtual portfolios and double-entry accounting | current | D8 |
| Simulated orders and forward paper evaluation | current | D9 |
| Point-in-time ML datasets and feature catalog | active implementation | D10 |
| Model registry, approval, explainability, and drift | planned | D11 |
| Evidence-backed recommendations | gated | D12; explicit user enablement |
| Local generative-AI assistant | gated | D13; user-managed runtime |
| Cloud generative-AI assistant | gated | D13; user credentials and provider governance |
| Alerts and typed scheduled workflows | planned | D14 |
| Optional personal server | gated | D14; secure configuration |
| Reports and governed exports | planned | D15 |
| Trusted-local desktop extensions | gated | D16; explicit permissions and evidence |
| Windows x86-64 desktop distribution | planned | D17 |
| Signed stable desktop release | planned | D19 |
| Live broker/exchange order submission | prohibited | Permanent no-go |
| Real-capital or unattended real trading | prohibited | Permanent no-go |
| Automatic model promotion | prohibited | Human approval required |
| AI as numerical or accounting authority | prohibited | Deterministic authority required |
| Generic frontend filesystem, shell, or database authority | prohibited | Python application and narrow Rust host boundaries |
| Unreviewed hostile-code extension sandbox claims | prohibited | No false containment guarantees |

Capabilities not listed here are unavailable until added through an accepted decision, requirement, and milestone update.
