# Why OSCA Is Built This Way

OSCA is designed for a long-lived, extensible system in which humans and AI agents can change behavior without steadily eroding trust.

Intent comes first because implementation is not a reliable source of product truth. Requirements make desired behavior reviewable. ADRs make expensive constraints explicit. Specifications translate both into a bounded change that can be verified.

Capability ownership exists to keep business meaning, state, and change authority together. A modular monolith gives the project clear boundaries and simple deployment without pretending that every boundary needs a network. Public seams preserve replacement and extension points without exposing internal structures.

Communication semantics are explicit because direct calls, commands, events, and workflows solve different problems. Events are reliable through durable recording, at-least-once delivery, scoped ordering, and idempotent consumers rather than fragile claims of universal exactly-once processing.

Compatibility is governed because retained workflows, extensions, analysis results, exports, and audit evidence may outlive the code that produced them. Exact revisions and migration provenance make historical behavior explainable.

Extensions are isolated according to trust because ecosystem openness must not grant third-party code ambient authority. Installation, activation, permissions, health, and quarantine are product capabilities, not informal conventions.

Persistence belongs to capabilities because shared tables otherwise become hidden APIs. Physical co-location is allowed; logical ownership is not shared. Reporting uses projections rather than bypassing domain boundaries.

Security, observability, and recovery are designed from the beginning because they cannot be added credibly after failures occur. Secure authenticated communication, least privilege, structured telemetry, separate audit evidence, compatible backups, and exercised restoration are part of correctness.

Quality gates are risk tiered because uniform gates are either too weak for dangerous changes or too expensive for routine ones. Evidence must be credible, retained, and proportional to impact.

Finally, architecture is intended to become executable. Documentation states the rules; validators, compatibility tests, dependency checks, security checks, recovery exercises, and telemetry conformance tests will increasingly enforce them. This allows AI assistance to increase delivery capacity without making reviewability, ownership, or long-term maintainability optional.
