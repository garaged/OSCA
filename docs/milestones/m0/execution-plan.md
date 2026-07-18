# M0 Execution Plan

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval role:** Product authority
- **Purpose:** Order M0 work so foundational decisions are made before dependent artifacts.
- **Authoritative sources:** M0 intent, M0 scope, PRD section 39
- **Downstream consumers:** M0 reviews, incremental commits, completion checklist, and exit evidence

## Increment sequence

### Increment 1 — Governance control plane

Establish M0 control documents, document governance, requirements authority, traceability model, ADR infrastructure, and milestone templates.

### Increment 2 — Ubiquitous language and system understanding

Create the glossary, system context, external actor and dependency inventory, domain model, and domain-language governance.

### Increment 3 — Architecture foundation

Define architecture principles, modular-monolith capability boundaries, dependency rules, consistency principles, and local versus personal-server topology constraints.

### Increment 4 — Draft seams

Specify the responsibilities, inputs, outputs, failure behavior, provenance obligations, compatibility rules, and security boundaries for provider, analysis, visualization, model, and extension seams.

### Increment 5 — Architecture decisions

Record consequential decisions that are sufficiently understood. Maintain explicit decision criteria and deferred-decision records for technology choices that are not ready.

### Increment 6 — Engineering lifecycle and standards

Specify SDD, IDD, TDD, acceptance criteria, test taxonomy, coding, migration, documentation, review, and definition-of-done standards.

### Increment 7 — Security and risk foundation

Produce the threat model, trust boundaries, misuse cases, security requirements, and detailed initial risk register.

### Increment 8 — Verification and quality gates

Define CI stages, traceability validation, architecture fitness checks, security checks, reference datasets, deterministic fixtures, and benchmark methodology.

### Increment 9 — Repository and contribution model

Finalize repository structure, ownership rules, contribution workflow, artifact placement, and compatibility-review requirements.

### Increment 10 — M0 closure

Complete consistency review, baseline coverage, risk-treatment evidence, deferred-decision review, completion checklist, exit-evidence index, and proposed M1 entry criteria.

## Increment publication rule

Completed, internally consistent documentation increments are committed to `agent/m0-foundation`. No final pull request or merge is initiated before explicit approval of the complete M0 package.
