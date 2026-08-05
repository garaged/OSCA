# D13 Intent — AI Research Assistant and Natural-Language Evidence Access

## Outcome
Users can ask grounded questions about their governed OSCA evidence, compare results, request explanations, and generate research briefs through bounded local or optional cloud AI providers.

## Scope
User-managed local-runtime adapters, optional user-credentialed cloud adapters, provider-neutral routing, prompt and context policies, evidence retrieval, bounded tools, citations, budget controls, evaluation, and generated-content labeling.

## Non-goals
Bundling a model initially, autonomous research execution, numerical authority, direct database or filesystem access, recommendation eligibility decisions, or order creation.

## Dependencies
D6 evidence projects and D12 structured recommendations.

## Risks
Hallucination, prompt injection, sensitive-data disclosure, ungrounded summaries, provider cost, and local-runtime incompatibility.

## Exit intent
Generated output is downstream of cited evidence; tools are allow-listed and schema-validated; imported text cannot override system policy; local use requires user-managed runtime installation; cloud use requires explicit credentials and data-flow disclosure; failures cannot alter authoritative records.
