# M2 Provider Contract Delta

## ADDED Requirements

### Requirement: One provider acquisition contract

Every M2 daily provider adapter SHALL publish the same versioned capability, request, result, observation, and failure semantics.

#### Scenario: Provider-specific limitation

- **WHEN** a provider has different authentication, quota, timestamp, rights, or quality limitations
- **THEN** the adapter expresses them as capability/policy metadata without changing canonical contract meaning

### Requirement: Offline deterministic conformance

Stock and crypto fixture adapters SHALL pass the same deterministic conformance suite without live networking or credentials.

#### Scenario: Rights uncertainty

- **WHEN** retrieval rights are false or uncertain
- **THEN** the adapter returns a policy failure and no observations
