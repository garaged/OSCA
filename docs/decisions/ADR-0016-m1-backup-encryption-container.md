# ADR-0016 — M1 Backup Encryption Container

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Security authority and architecture authority
- **Scope:** M1 backup creation, verification, preview, and isolated restore
- **Related requirements:** REQ-0010, REQ-0013, REQ-0017, REQ-0018
- **Related product decisions:** D-031
- **Supersedes:** DD-012 for the M1 backup format
- **Superseded by:** None

## Context

The accepted M1 specification prohibits exposing or merging a production backup command until an interoperable reviewed encryption container is selected. Backup content includes configuration references, workflow state, catalog records, and audit metadata, so confidentiality, integrity, compatibility, and recoverability must not depend on an OSCA-specific cryptographic format.

## Decision drivers

- Interoperability across supported local platforms and independent implementations.
- Authenticated encryption with safe corruption and wrong-identity failure.
- Recipient-based encryption that does not place private identity material in configuration, manifests, logs, or backup content.
- Streaming operation and a small, reviewable integration boundary.
- Explicit format/version identity for compatibility checks and future migration.

## Considered alternatives

### age v1 with X25519 recipients

**Benefits**

- Publicly specified interoperable format with independent implementations.
- Authenticated streaming encryption and explicit recipient identities.
- Public recipient material can configure backup creation while private identities remain vault-managed.
- Simple command-line adapter permits independent interoperability tests.

**Costs and risks**

- The reference executable is an external runtime prerequisite until a reviewed native adapter is selected.
- Recipient rotation requires deliberate operational guidance and retained recovery identities.

### AES-encrypted ZIP

**Benefits**

- Familiar archive workflow and broad tool availability.

**Costs and risks**

- Multiple incompatible encryption profiles and inconsistent tooling defaults.
- Archive parsing and path handling broaden the attack surface.
- Password handling encourages secret material at the command boundary.

### OSCA-specific encrypted container

**Benefits**

- Full implementation control.

**Costs and risks**

- Prohibited ad-hoc cryptography, no independent interoperability, and long-term migration burden.

## Decision

M1 production backups SHALL use the binary age v1 format with standard X25519 recipients. Backup creation accepts validated public recipient strings only. Restore obtains private identity material through the Security capability's vault abstraction and supplies it to the age adapter without persisting or logging it.

OSCA SHALL invoke a compatible age implementation through a narrow, shell-free adapter with bounded input/output, timeout, safe environment, and stable error classification. The cleartext payload is a deterministic, size-limited archive staged in a private temporary location and removed on success or failure. Plaintext packages are permitted only as explicitly marked test fixtures and SHALL NOT be exposed by a production command.

The backup record and manifest identify the OSCA contract family and version, age format version, recipient fingerprints rather than private identities, source build, schema range, checksums, exclusions, and package digest. Authenticating/decrypting into private isolated staging precedes archive parsing or restore writes.

## Rationale

age v1 satisfies the M1 interoperability and authenticated-encryption requirements without creating an OSCA cryptographic scheme. X25519 recipients separate public backup configuration from private restore authority and fit the existing named-secret-reference model. A process adapter keeps cryptographic implementation outside OSCA while retaining testable boundaries.

## Consequences

### Positive

- Backups can be independently decrypted by conforming age implementations.
- Wrong identities and modified ciphertext fail before restore processing.
- Recipient public keys are not secrets; private identities remain vault-controlled.
- The container choice is explicit and migration-capable.

### Negative and tradeoffs

- Production backup and restore require an available compatible age executable.
- M1 must document identity custody, rotation, loss, and interoperability testing.
- Temporary cleartext staging must be permission-restricted and reliably cleaned.

### Required follow-up

- Recovery owns the process adapter and package lifecycle.
- Security owns identity-reference resolution and redaction conformance.
- Quality retains wrong-identity, tamper, timeout, cleanup, interoperability, and secret-canary evidence.
- Operations documents installation and recovery identity custody.

## Fitness and verification

- A package encrypted by OSCA decrypts with an independent compatible age CLI and vice versa.
- Wrong identity, corrupt header/payload, unsupported format, timeout, and unavailable executable fail closed with stable safe errors.
- Private identities and secret canaries are absent from arguments, environment captures, logs, audit details, manifests, package listings, and retained artifacts.
- No valid-looking final package remains after encryption failure.
- Temporary cleartext paths are private and removed after every outcome.
- Active-state digest is unchanged by verification, preview, and isolated restore.

## Migration and compatibility

The M1 container identifier is `age/v1+x25519`. Manifests declare readable OSCA product and schema ranges independently of the encryption format. Future containers require a new accepted ADR and explicit compatibility behavior; existing readable packages remain supported or receive a governed migration path.

## Risks

Identity loss makes encrypted backups unrecoverable; documentation and verification must require custody confirmation. Executable substitution is constrained by explicit configuration, version probing, shell-free invocation, and interoperability evidence. Malicious archives remain untrusted after decryption and require bounded, path-safe parsing.

## Revisit triggers

Managed hosting, multi-user recovery authority, hardware-backed age plugins, removal of the external executable, post-quantum recipient requirements, supported-platform incompatibility, or a material age specification/security change.
