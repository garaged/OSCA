# Engineering System Metrics Framework

Metrics are diagnostic signals, not delivery targets in isolation. They must not reward gaming, conceal risk, or replace qualitative review.

## Architecture health

- architecture fitness pass rate;
- dependency and persistence-boundary violations;
- public contract compatibility failures;
- foundational ADR supersessions and active exceptions;
- unresolved deferred decisions past their trigger.

## Quality and traceability

- accepted requirements with linked specifications and verification;
- risk-classification override frequency;
- escaped defects and added regression evidence;
- flaky test count and age;
- release evidence completeness.

## Delivery system

- lead time from accepted intent to verified vertical slice;
- review turnaround by risk tier;
- deterministic gate duration and failure causes;
- documentation and migration completion at merge;
- exception volume, age, and expiry compliance.

## Operational readiness

- telemetry-contract completeness;
- uncorrelated or improperly redacted telemetry findings;
- recovery exercise success and restoration verification;
- compatibility and replay regressions;
- extension validation, quarantine, and permission violations.

## Maturity interpretation

1. Documented
2. Traceable
3. Executable
4. Self-validating
5. Evidence-driven improvement

Maturity is assessed per area and must not be collapsed into an unsupported overall score. Implementation and production maturity remain zero until evidence exists.

## Reporting rules

Every metric has an owner, definition, collection method, review cadence, limitations, and action threshold. Trend and distribution are preferred over isolated point values. Metrics involving people are reviewed for harmful incentives before adoption.
