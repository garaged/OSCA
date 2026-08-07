# Asset Catalog and Watchlists

## ADDED Requirements

### Requirement: Canonical asset identity
The desktop application SHALL expose stable canonical asset identifiers that remain separate from provider aliases.

#### Scenario: Provider alias resolves to canonical identity
- **WHEN** a user searches for `BTC`
- **THEN** the result identifies `crypto:KRAKEN:XBTUSD` as the canonical asset
- **AND** the provider alias remains visible as provenance rather than replacing the canonical identifier

### Requirement: Deterministic offline market search
The desktop application SHALL search bundled and locally retained asset metadata without a network request and SHALL return stable ordering for equivalent inputs.

#### Scenario: Exact symbol collision is visible
- **WHEN** multiple venues contain the exact symbol `ABC`
- **THEN** the search result marks the query as ambiguous
- **AND** each candidate includes venue, name, asset class, and canonical identifier

### Requirement: Profile-scoped persistent watchlists
The desktop application SHALL persist watchlists and ordered canonical memberships inside the selected profile.

#### Scenario: Watchlist survives restart
- **WHEN** a user creates a watchlist, adds canonical assets, and reorders them
- **THEN** reopening the same profile returns the same watchlist and order
- **AND** opening another profile does not expose those memberships

### Requirement: Narrow typed desktop authority
React SHALL use only the existing `desktop_request` bridge and Python SHALL remain authoritative for asset search, details, recent assets, watchlist validation, persistence, and mutation locking.

#### Scenario: Watchlist mutation is locked
- **WHEN** another process holds the profile mutation lock
- **THEN** a watchlist mutation fails with a typed lock error
- **AND** no partial watchlist state is committed

### Requirement: Accessible responsive Markets surface
The desktop application SHALL provide keyboard, focus, reduced-motion, forced-colors, screen-reader, and narrow-layout safeguards for the Markets surface.

#### Scenario: Narrow market browser remains usable
- **WHEN** the viewport is 320 CSS pixels wide
- **THEN** the asset browser and watchlists stack without horizontal loss of controls
- **AND** canonical identity and ambiguity information remain perceivable

### Requirement: Permanent safety boundaries
D4 SHALL NOT add streaming quotes, charting, recommendations, portfolio ownership, brokerage connectivity, or order execution.

#### Scenario: Offline search preserves execution boundary
- **WHEN** a user searches assets or edits watchlists
- **THEN** no provider network request or execution method is invoked
- **AND** the interface continues to state that the workflow is research-only
