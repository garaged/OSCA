# Contributor Security Review

Use this review for changes that affect extension trust, provider access, credentials, storage, evidence, network behavior, serialization, package installation, or execution boundaries.

## Trust and execution

- [ ] The change identifies every new trust boundary.
- [ ] Untrusted input is validated before use.
- [ ] Extension validation does not import or execute code.
- [ ] Trusted-local acceptance remains an explicit human decision.
- [ ] No public marketplace, remote installation, or automatic update path is introduced.

## Capabilities

- [ ] Requested capabilities are explicit and minimal.
- [ ] Unknown capabilities fail closed.
- [ ] Broker, exchange order, recommendation, live-serving, real-capital, and remote-write capabilities remain prohibited.
- [ ] Network and credential access are disabled unless separately governed by an accepted authority.

## Integrity and provenance

- [ ] Every extension artifact is declared and SHA-256 verified.
- [ ] Paths are relative and cannot escape the package root.
- [ ] Source repository, full source commit, version, and SPDX license are retained.
- [ ] Generated or downloaded content is not silently trusted.

## Data and evidence

- [ ] No credentials, secrets, private datasets, or generated evidence are committed.
- [ ] Provider licensing and redistribution restrictions remain attached to retained evidence.
- [ ] Corrupt, incomplete, or mismatched artifacts fail closed.

## Compatibility

- [ ] API compatibility is checked before execution.
- [ ] Breaking changes require a new major API version and migration authority.
- [ ] Deprecations include replacement guidance and a support window.

## Validation

- [ ] Hostile and malformed inputs have regression tests.
- [ ] The canonical contributor validation passes on supported hosted platforms.
- [ ] Security-sensitive failure messages are actionable without exposing secrets.
