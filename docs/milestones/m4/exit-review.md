# M4 Exit Review

- **Milestone:** M4 research projects, analytics, and visualization
- **Status:** Accepted for PR review
- **Branch:** `agent/m4-research-projects-analytics`
- **Last reviewed:** 2026-07-24

## Scope accepted

M4 starts from the completed M3 temporal correctness baseline and adds the governed exploratory research layer above market data.

Accepted M4 scope includes:

- Research project, hypothesis, timeline, ad hoc workspace, and promotion contracts.
- Hypothesis lifecycle transition behavior with timeline evidence.
- Analysis graph contracts, validation, and deterministic planning.
- Analytical output provenance contracts.
- Evidence-report assembly.
- Declarative visualization specifications and export metadata.
- Dashboard composition from governed visualization specifications.
- Requirements, traceability, OpenSpec, documentation, and retained evidence for REQ-0053-REQ-0068.

## Deferred scope

The following remain outside M4 and require later governed milestone intents:

- Independent extension packaging and activation.
- Strategy research and backtesting.
- Paper trading and live execution.
- ML lifecycle and LLM-assisted analysis.
- Provider production promotion for paid, authenticated, or license-sensitive use.

## Exit decision

M4 is complete for the accepted scope once the final archived-head hosted Quality run passes OpenSpec strict validation, secret scan, Ruff, strict mypy, pytest, contracts, migrations, documentation links, and architecture validation.
