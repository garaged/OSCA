# Architecture and Pull-request Review Checklist

- **Status:** Accepted control
- **Governing role:** Quality authority
- **Architecture approval:** Architecture authority where triggered
- **Last reviewed:** 2026-07-18

- [ ] The change states intent, requirement IDs, specification, ADRs, and risk class.
- [ ] Capability ownership and interaction classification are explicit.
- [ ] No private cross-module dependency or persistence access is introduced.
- [ ] Public contracts are intentional, cataloged, compatible, and owned.
- [ ] Failure, retry, cancellation, idempotency, degradation, and recovery are covered.
- [ ] Authorization denial paths, secure transfer, secrets, and sensitive-data handling are covered.
- [ ] Telemetry, correlation, audit, redaction, health, and diagnostics are covered.
- [ ] Migration, rollback/forward recovery, and historical artifacts are addressed.
- [ ] Verification matches risk and includes credible negative/failure evidence.
- [ ] Documentation, indexes, traceability, and evidence records change with behavior.
- [ ] Deferred decisions were not resolved implicitly.
- [ ] Exceptions are approved, narrow, detected, and expiring.
- [ ] Remaining risks and deferred work have owners and triggers.

A checked box is a review assertion and must be supported by the diff or linked evidence.
