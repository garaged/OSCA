# Desktop Milestone Specification Template

Use this template when a desktop milestone moves from accepted intent to implementation.

## Authority

- Milestone:
- Status:
- Approved intent:
- Governing decisions and ADRs:
- Product-traceability rows:
- Dependencies and baseline commit:

## Problem and user outcome

Describe the user problem, observable outcome, and why this milestone is needed now.

## Scope

List the capabilities delivered in this milestone.

## Non-goals and prohibited behavior

State explicit deferrals and permanent boundaries, including the no-live-order rule where relevant.

## Functional requirements

Use stable requirement identifiers and testable language.

## Quality requirements

Apply `docs/product/cross-cutting-requirements.md` and add milestone-specific security, accessibility, performance, reliability, privacy, localization, and portability requirements.

## Architecture and contracts

Document application-service boundaries, IPC/API schemas, storage ownership, provider capabilities, extension permissions, and failure behavior. Frontend calculations must remain presentation-only.

## Data and migration

Describe schemas, revisions, backup, preflight, forward migration, interruption recovery, rollback or restore behavior, and compatibility with existing U14 profiles.

## UX and state model

Cover primary journeys, empty/loading/degraded/error states, keyboard and screen-reader behavior, confirmation boundaries, and unavailable-capability explanations.

## Testing

Define TDD slices, unit/property/golden/integration/IPC/UI/accessibility/security tests, hosted gates, and clean-profile manual acceptance.

## Documentation updates

List user guide, methodology, provider, troubleshooting, architecture, OpenSpec, traceability, migration, manual-testing, and limitation updates.

## Risks and decisions

Record risks, mitigations, evidence-gated choices, and any decision that must be approved before proceeding.

## Exit criteria

A milestone exits only when every requirement is implemented or explicitly deferred through an accepted decision, all required gates pass, manual evidence is retained, and the exit review reconciles architecture and traceability.
