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

### Requirement: Window-scoped opened-profile ownership
A successfully opened profile SHALL be owned by the desktop window/session that opened it until that window closes or leaves the opened profile. Remembering or selecting a profile SHALL NOT grant mutation authority.

#### Scenario: Second window cannot take over an opened profile
- **GIVEN** window A has successfully opened profile A
- **WHEN** window B attempts to open profile A
- **THEN** window B fails closed with a profile-in-use or ownership-conflict error
- **AND** window A remains bound to profile A
- **AND** no watchlist, recent-asset, ordering, or profile metadata is changed

#### Scenario: Selection alone cannot mutate an owned profile
- **GIVEN** window A owns profile A
- **AND** window B only selects profile A
- **WHEN** window B attempts a profile-scoped mutation
- **THEN** the mutation is rejected before profile state is changed
- **AND** window A can continue valid mutations

#### Scenario: Supported non-UI mutation cannot bypass desktop ownership
- **GIVEN** a desktop window holds the lifetime session lease for profile A
- **WHEN** a supported Python/CLI desktop-API mutation targets profile A outside that broker-owned window
- **THEN** the mutation fails with a typed `profile_locked` error
- **AND** no profile-scoped state is changed
- **AND** the owning desktop window remains usable

#### Scenario: Broker-owned sidecar can mutate its own leased profile
- **GIVEN** a desktop window owns profile A
- **WHEN** the broker invokes the short-lived Python sidecar for an authorized mutation of profile A
- **THEN** the sidecar reuses the broker ownership context rather than deadlocking on the session lease
- **AND** the normal bounded Python mutation lock still serializes the write

#### Scenario: Ownership is released with the owning window
- **GIVEN** window A owns profile A
- **WHEN** window A closes or explicitly leaves profile A
- **THEN** another window can subsequently open profile A
- **AND** a supported non-UI mutation can subsequently acquire the profile when no desktop owner exists

#### Scenario: One window does not silently adopt another window's profile
- **GIVEN** window A owns profile A
- **WHEN** window B opens or selects profile B
- **THEN** window A continues to report profile A as its active opened profile

### Requirement: Narrow typed desktop authority
React SHALL use only the existing `desktop_request` bridge and Python SHALL remain authoritative for asset search, details, recent assets, watchlist validation, persistence, and bounded mutation validation. The persistent Rust desktop broker MAY enforce only the window/session ownership and lifetime lock needed to preserve that Python-authoritative contract across short-lived sidecar requests.

#### Scenario: Watchlist mutation is locked
- **WHEN** another process holds the bounded profile mutation lock
- **THEN** a watchlist mutation fails with a typed lock error
- **AND** no partial watchlist state is committed

#### Scenario: Broker rejects non-owner mutation
- **GIVEN** a desktop window has not opened the target profile
- **WHEN** it submits a watchlist or recent-asset mutation for that profile
- **THEN** the persistent desktop broker rejects the request
- **AND** the Python sidecar is not used to bypass window ownership

### Requirement: Self-contained native desktop service
Native OSCA packages SHALL include the Python desktop sidecar needed by the Tauri broker and SHALL NOT require a separately started development server, repository checkout, active virtual environment, or system-installed `osca` package for normal packaged operation.

#### Scenario: Packaged application starts its bundled sidecar
- **GIVEN** a native OSCA package built for a supported platform
- **WHEN** the packaged application is launched directly outside development mode
- **THEN** the broker invokes the bundled target-specific sidecar automatically
- **AND** desktop bootstrap succeeds without `make run`, a manually started Python service, or `OSCA_DESKTOP_PYTHON`
- **AND** Markets and profile-scoped watchlists remain usable

#### Scenario: Development interpreter override remains supported
- **GIVEN** the repository development launcher explicitly supplies `OSCA_DESKTOP_PYTHON`
- **WHEN** the Tauri development application invokes the desktop service
- **THEN** the broker uses that locked development interpreter rather than the packaged sidecar

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
