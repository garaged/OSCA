# AI Contributor Contract

AI-assisted work is governed by the same requirements, architecture, security, quality, and review obligations as human-authored work.

## Required input context

An implementation request should identify or resolve:

- intent and requirement identifiers;
- owning capability;
- applicable ADRs and specifications;
- affected public contracts;
- compatibility, migration, security, observability, and recovery constraints;
- expected verification evidence.

An agent must inspect authoritative repository artifacts rather than rely on conversation summaries when changing governed behavior.

## Required delivery report

Every implementation response must report:

- files changed;
- design rationale and interaction classification;
- public contracts added or changed;
- requirements and ADRs addressed;
- tests and verification executed;
- migrations and compatibility impact;
- security, observability, and recovery impact;
- risks, assumptions, deferred work, and suggested review focus.

## Prohibited behavior

An AI contributor must not:

- invent product requirements to unblock implementation;
- weaken accepted requirements or ADRs silently;
- bypass capability boundaries or persistence ownership;
- introduce a public contract accidentally;
- claim verification that was not performed;
- hide uncertainty, failing checks, or incomplete work;
- treat generated code as exempt from review;
- embed secrets or sensitive data in prompts, fixtures, logs, or examples.

## Change discipline

Prefer small, traceable vertical slices. Update specifications and tests before or with behavior changes. Add regression evidence for every corrected defect. Stop for approval only when a genuinely consequential unresolved decision is reached; otherwise continue within accepted authority.

## Review focus

Reviewers should concentrate on intent alignment, ownership, contract evolution, failure behavior, security boundaries, telemetry completeness, recovery impact, and the credibility of verification evidence—not merely code style.


## OpenSpec pilot

When an active change is managed by OpenSpec, an AI contributor must read its proposal, delta specs, design, and tasks together with the governing OSCA artifacts. Task completion is an evidence assertion. OpenSpec cannot invent authority, waive gates, or replace the required delivery report. See the [integration policy](../docs/governance/openspec-integration.md).
