# M10 LLM Lifecycle and Gateway Specification

- **Status:** Draft
- **Milestone:** M10
- **Requirements:** REQ-0125-REQ-0133
- **ADR:** ADR-0036
- **Manual testing:** M10 updates `docs/testing/manual-testing.md`

## Requirements

### Provider-neutral LLM route

LLM requests must preserve provider, model, capability, privacy, cost, latency, and availability routing evidence without silently substituting model versions.

### Bounded LLM tools

LLM tools must be narrow typed application capabilities with explicit read or state-changing mode, permission scope, and live-order prohibition.

### Versioned prompt and tool contracts

Prompt templates, tool definitions, context-selection policies, model/provider configuration, and structured outputs must be versioned and schema-validated.

### Explicit project context

LLM context policies must identify selected project context and approved global references and must not silently mix unrelated project histories.

### Privacy and untrusted-content boundary

LLM requests must preserve privacy classification and untrusted external-content handling, and sensitive disclosure must fail closed when not approved.

### LLM budget enforcement

LLM request contracts must declare token, monetary, latency, and tool-call budgets, and routing must fail closed when estimated cost exceeds budget.

### LLM evaluation evidence

LLM evaluation reports must preserve factual grounding, citation, numerical consistency, structured-output validity, refusal, boundary, injection-resistance, tool-use, cost, and latency findings as applicable.

### Manual testing

M10 must review and update the manual testing and usage baseline for LLM gateway operator-visible behavior.

### Metadata persistence

LLM lifecycle metadata must persist provider capabilities, prompts, tools, context policies, requests, route decisions, and evaluation reports with request-scoped queries without executing provider calls.
