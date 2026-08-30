# Desktop Acceptance Automation Proposal

## Why

Desktop D5--D8 acceptance has accumulated repeatable setup and verification work that consumes disproportionate human time. The same governed local workflow can be exercised deterministically before a reviewer performs the visual and exploratory checks that actually need judgment.

## What changes

- provide a reset-safe command that creates a disposable, deterministic desktop acceptance profile;
- exercise D5 comparison, D6 project evidence, and D7 strategy/backtest/evaluation paths through the typed desktop service;
- retain a machine-readable acceptance manifest;
- expand the focused desktop suite through D8; and
- replace repeated D5--D7 setup instructions with a ten-minute changed-surface human smoke test.

## Non-goals

Browser automation, a new UI-driver dependency, visual-pixel baselines, provider access, credentials, broker connections, recommendations, autonomous execution, or real-capital behavior.
