# M2 Instrument Registry Delta

## ADDED Requirements

### Requirement: Provider-neutral instrument registration

The system SHALL persist immutable versioned stock and crypto-pair references whose canonical identity is independent of provider symbols.

#### Scenario: Duplicate identity

- **WHEN** registration supplies an existing canonical identity under a different display symbol
- **THEN** registration fails without creating another instrument

### Requirement: Governed provider mapping

The system SHALL activate only verified, time-aware mappings whose provider alias is unambiguous for the applicable interval.

#### Scenario: Ambiguous alias

- **WHEN** a verified alias overlaps a different canonical instrument
- **THEN** mapping activation fails before any canonical market-data write
