# p14-production-operations Specification

## Purpose

Define explicit personal-server operations with fail-closed security and retained evidence.

## Requirements

### Requirement: Secure personal-server exposure

P14 SHALL reject non-loopback binding unless TLS and authentication are both enabled.

#### Scenario: Unsafe external binding is requested
- **GIVEN** a personal-server configuration without TLS or authentication
- **WHEN** a non-loopback host is selected
- **THEN** validation fails before the service is exposed.

### Requirement: Explicit scheduled execution

P14 SHALL execute only explicitly enabled scheduled commands with a bounded timeout and retained stdout/stderr evidence.

#### Scenario: Disabled job is evaluated
- **GIVEN** a configured but disabled job
- **WHEN** execution is requested
- **THEN** OSCA returns `policy_blocked` without launching the command.

#### Scenario: Enabled job completes
- **GIVEN** an explicitly enabled job
- **WHEN** the command completes
- **THEN** OSCA records status, exit code, timing, stdout, stderr, and findings.

### Requirement: Explicit alert delivery

P14 SHALL deliver alerts only through enabled file or HTTPS-webhook transports and SHALL redact webhook destinations in evidence.

#### Scenario: Alert transport is disabled
- **GIVEN** a configured alert without explicit enablement
- **WHEN** delivery is requested
- **THEN** OSCA returns `policy_blocked` without writing or calling a webhook.

### Requirement: Off-source backup and validated restore

P14 SHALL create backup archives outside the source tree with manifests and SHA-256 evidence, and SHALL restore through path-safe staging.

#### Scenario: Backup destination is inside the source tree
- **GIVEN** an enabled backup request
- **WHEN** its destination is the source or a descendant
- **THEN** OSCA returns `policy_blocked` without creating an archive.

#### Scenario: Restore destination is non-empty
- **GIVEN** a valid archive and non-empty restore destination
- **WHEN** overwrite permission is absent
- **THEN** OSCA returns `policy_blocked` without replacing files.

### Requirement: Hardened deployment examples

P14 SHALL provide single-user systemd service and timer templates with common hardening directives while documenting operator-owned controls.

#### Scenario: Deployment template is reviewed
- **GIVEN** the P14 deployment files
- **WHEN** an operator reviews them
- **THEN** least privilege, restricted write paths, no-new-privileges, and timer persistence are visible.

### Requirement: P14 completion evidence

P14 SHALL retain requirements, traceability, manual usage, automated validation, OpenSpec, and hosted Quality evidence.

#### Scenario: P14 completion is requested
- **GIVEN** P14 implementation work
- **WHEN** completion is evaluated
- **THEN** exit evidence identifies implemented behavior, operator-owned controls, remaining deferrals, and final validation results.
