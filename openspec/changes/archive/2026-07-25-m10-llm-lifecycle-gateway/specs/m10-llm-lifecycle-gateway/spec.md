# m10-llm-lifecycle-gateway Specification

## ADDED Requirements

### Requirement: Provider-neutral LLM route

LLM route decisions SHALL preserve exact provider identity, model identity, requested capability, privacy class, budget evidence, and routing rationale without silently substituting model versions.

#### Scenario: Provider cannot satisfy requested capability
- **WHEN** no provider capability supports the requested LLM capability and privacy class
- **THEN** route evaluation fails closed

### Requirement: Bounded LLM tools

LLM tools SHALL declare tool identity, version, mode, permission scope, and live-order prohibition.

#### Scenario: Tool declares live-order capability
- **WHEN** an LLM tool definition declares live-order capability
- **THEN** validation fails closed

### Requirement: Versioned prompt and tool contracts

Prompt templates, tool definitions, context policies, provider configuration, and structured outputs SHALL carry stable version identities.

#### Scenario: Prompt template omits version
- **WHEN** a prompt template omits a stable version
- **THEN** validation fails closed

### Requirement: Explicit project context

LLM context policies SHALL identify selected project context and approved references.

#### Scenario: Context policy omits project identity
- **WHEN** an LLM context policy omits selected project identity
- **THEN** validation fails closed

### Requirement: Privacy and untrusted-content boundary

LLM route evaluation SHALL fail closed when sensitive disclosure is requested without approval or untrusted content handling is disabled.

#### Scenario: Sensitive disclosure lacks approval
- **WHEN** an LLM request requires sensitive disclosure without approval
- **THEN** route evaluation fails closed

### Requirement: LLM budget enforcement

LLM route evaluation SHALL reject requests whose estimated monetary cost exceeds the declared budget.

#### Scenario: Estimated cost exceeds budget
- **WHEN** estimated cost is greater than the request budget
- **THEN** route evaluation fails closed

### Requirement: LLM evaluation evidence

LLM evaluation reports SHALL preserve evaluation dimensions, findings, cost, latency, and evaluated time.

#### Scenario: Passed evaluation contains error finding
- **WHEN** an LLM evaluation report is marked passed and contains an error finding
- **THEN** validation fails closed

### Requirement: M10 manual testing update

M10 SHALL review and update the manual testing and usage baseline for LLM gateway operator-visible behavior.

#### Scenario: M10 changes operator-visible LLM behavior
- **WHEN** M10 adds LLM lifecycle contracts or usage surfaces
- **THEN** the manual testing and usage baseline includes M10-specific smoke checks

### Requirement: LLM lifecycle metadata persistence

LLM lifecycle metadata SHALL persist provider capabilities, prompts, tools, context policies, requests, route decisions, and evaluation reports with request-scoped queries without executing provider calls.

#### Scenario: LLM lifecycle records are persisted
- **WHEN** LLM lifecycle records are saved
- **THEN** they can be queried by request identity without invoking a provider
