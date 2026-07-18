# LLM Seam

- **Status:** Draft
- **Owner:** LLM gateway capability
- **Purpose:** Provide bounded, provider-neutral language-model synthesis and tool use without granting authority over deterministic financial facts or unrestricted application state.

## Contract groups

- task and capability declaration;
- provider and model routing policy;
- prompt, system-instruction, retrieval, and context-selection definitions;
- typed application-tool schemas and permission requirements;
- structured-output schema and validation;
- run record, citations, budgets, tool calls, and evaluation results.

## Mandatory behavior

- LLMs use approved application tools, never private databases or internal module services.
- Read and state-changing tools are distinct; imported workflows receive no state-changing authority by default.
- External content and extension output are untrusted data, not privileged instructions.
- Structured outputs are schema-validated before use.
- Claims reference governed observations or identified external sources; unsupported claims are labeled as hypotheses.
- Model, provider, prompt, tool, context policy, permissions, and budgets are retained in provenance.
- Sensitive disclosure is previewable and controllable.
- Token, monetary, latency, and tool-call limits fail safely.
- No tool can place a live order.

## Conformance evidence

Tests cover prompt injection, unauthorized tools, malformed structured output, numerical inconsistency, unsupported claims, sensitive-data disclosure, budget exhaustion, provider fallback, citation integrity, and stable refusal behavior.