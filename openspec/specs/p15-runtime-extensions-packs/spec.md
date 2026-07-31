# p15-runtime-extensions-packs Specification

## Purpose

Define the governed trusted-local runtime extension path for P15.

## Requirements

### Requirement: Trusted local pack validation

P15 SHALL validate exact pack identity, semantic version, compatibility, trust tier, executable SHA-256 digest, and declared permissions before installation or execution.

#### Scenario: A tampered or untrusted pack is supplied
- **GIVEN** a pack with a digest mismatch or an untrusted/quarantined trust tier
- **WHEN** validation is requested
- **THEN** OSCA returns a failed or policy-blocked result before executing the pack.

### Requirement: Explicit permission approval

P15 SHALL require the approved permission set to exactly match the manifest permission set.

#### Scenario: Permission approval differs from the manifest
- **GIVEN** a pack requesting permissions
- **WHEN** the operator-approved set is missing, additional, or different
- **THEN** OSCA reports `policy_blocked` and does not execute the pack.

### Requirement: Bounded subprocess execution

P15 SHALL execute trusted packs only after explicit enablement, through a direct subprocess without a shell, with bounded runtime, bounded output, minimized environment, and JSON-object output validation.

#### Scenario: Execution is not enabled
- **GIVEN** a valid trusted pack
- **WHEN** execution is requested without explicit enablement
- **THEN** OSCA returns `policy_blocked` and does not start the subprocess.

#### Scenario: A pack completes successfully
- **GIVEN** a valid trusted pack with exact permission approval
- **WHEN** explicitly enabled execution returns a JSON object within budgets
- **THEN** OSCA returns `succeeded` and retains stdout, stderr, digest, exit code, package version, and findings.

### Requirement: Versioned installation and rollback

P15 SHALL install validated versions under an explicit package/version path and SHALL roll back only to an already installed version.

#### Scenario: Rollback targets an installed version
- **GIVEN** two validated installed versions of one package
- **WHEN** rollback targets the older version
- **THEN** OSCA updates the active-version pointer and retains rollback evidence.

#### Scenario: Rollback targets a missing version
- **GIVEN** no installed target version
- **WHEN** rollback is requested
- **THEN** OSCA fails closed without changing the active pointer.

### Requirement: P15 deferred-boundary enforcement

P15 SHALL NOT enable public marketplaces, remote discovery, in-process arbitrary imports, untrusted-code execution, implicit permission renewal, provider-scope expansion, credentials, brokers, autonomous trading, or real-capital orders.

#### Scenario: Deferred behavior is attempted
- **GIVEN** a P15 runtime pack request
- **WHEN** the request depends on behavior outside the accepted trusted-local subprocess scope
- **THEN** OSCA fails closed or leaves the behavior unavailable.

### Requirement: P15 completion evidence

P15 SHALL retain requirements, traceability, manual usage, conformance tests, OpenSpec, exit review, and hosted Quality evidence.

#### Scenario: P15 completion is requested
- **GIVEN** the P15 implementation candidate
- **WHEN** completion is evaluated
- **THEN** implemented and deferred behavior plus final validation evidence are recorded.
