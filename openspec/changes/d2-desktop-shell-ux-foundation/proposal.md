# Proposal: D2 Desktop Shell and User Experience Foundation

## Why

D1 established the Tauri/React/Rust/Python architecture and a minimal health vertical slice, but the desktop remains a developer preview. New users cannot yet complete an honest offline first run, manage validated profiles, distinguish unavailable capabilities, or inspect system state through a reusable accessible shell.

## What changes

- Add a responsive desktop shell with Home and System as real destinations.
- Expose later Research and Evidence destinations only as explicit unavailable states.
- Add first-run disclosures and persistent research-only/no-live-execution boundaries.
- Add versioned Python desktop methods for profile list, inspect, create, select, and open.
- Add bounded profile mutation locks and versioned desktop preference state.
- Add typed system diagnostics and explicit loading, empty, unavailable, retry, blocked, and app-error handling.
- Add deterministic bundled synthetic OHLCV import through the canonical Python import service.
- Add reusable semantic UI tokens, keyboard/focus foundations, reduced-motion, light/dark, and forced-colors support.
- Add automated Python, frontend, architecture, and Rust gates plus clean-profile manual acceptance.

## Non-goals

D2 does not add provider or credential setup, provider acquisition, production research/evidence workbenches, recommendations, model execution, broker or exchange connectivity, autonomous execution, live-order submission, real-capital orders, or generic frontend/Rust filesystem and shell access.

## Exit outcome

A new user can launch OSCA, understand the product boundaries, create or open a validated local profile, import deterministic synthetic sample data entirely offline, and inspect system state through a responsive keyboard-accessible desktop shell while Python remains authoritative and every financial/execution boundary remains fail closed.
