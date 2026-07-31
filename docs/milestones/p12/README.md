# P12 - Local Model-Assisted Preview

- **Status:** Complete through PR #55
- **Governing role:** Product authority
- **Phase:** Useful analyst workflow
- **Authoritative outcome:** Add opt-in, evidence-retaining local model previews with explicit budgets and fail-closed LLM boundaries.
- **Baseline:** Completed M0-M12 roadmap and P1-P11
- **Last reviewed:** 2026-07-31
- **Validation:** Final Quality run `30646021643`; merge commit `03aca9f71db0087c2ef6df5b176baae219cbf99e`

## Implemented outcome

P12 provides deterministic local ordinary-least-squares trend evidence and fixture-backed LLM analysis with exact model/prompt identity, explicit budgets, atomic evidence retention, mandatory human review, and fail-closed live-model behavior.

## Preserved boundaries

Remote model invocation, credential resolution, production model serving, automated model promotion, recommendations, brokers, autonomous actions, and real-capital orders remain disabled. P12 remains optional and does not replace the deterministic P6-P11 workflow.

## Validation evidence

- Ruff passed.
- Strict mypy passed across 193 source files.
- 324 tests passed, including all seven P12 tests.
- Contracts, migrations, links, architecture, OpenSpec, and secret scanning passed.
