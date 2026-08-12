# D4 Specification — Asset Catalog, Market Browser, and Watchlists

## 1. Canonical asset identity

Each asset has a stable profile-local identifier independent from provider symbols. The canonical record includes asset class, canonical symbol, display name, venue when applicable, quote currency when applicable, aliases, provenance, lifecycle status, and timestamps.

Provider aliases map to canonical assets and never become the primary identity. Ambiguous aliases return an explicit ambiguity result instead of silently selecting an asset.

## 2. Catalog sources

The catalog is composed from:

- bundled deterministic seed assets;
- assets observed in governed local imports;
- assets observed in admitted historical acquisitions;
- explicit user registration;
- optional admitted-provider enrichment in later slices.

Catalog browsing and watchlists must remain usable offline.

## 3. Search and filtering

Search is deterministic and case-insensitive across canonical symbol, display name, aliases, venue, and quote currency. Filters include asset class, lifecycle state, venue, and local-data availability.

Results are ordered by exact canonical-symbol match, exact alias match, prefix match, then normalized display-name match. Stable identifiers break ties.

## 4. Availability summary

Asset detail exposes local evidence only: known datasets, available timeframes, earliest and latest retained observation, provider/source provenance, and freshness classification derived from stored metadata. The UI must not imply streaming or real-time availability.

## 5. Watchlists

Watchlists are profile-scoped entities with stable identifiers, unique normalized names, optional descriptions, explicit ordering, and ordered canonical asset memberships.

Supported operations:

- create;
- list;
- rename and edit description;
- delete;
- add or remove an asset;
- reorder assets;
- reorder watchlists.

All mutations are transactional and idempotent where practical. Deleting a watchlist does not delete assets or market data.

## 6. Persistence, profile ownership, and recovery

SQLite is authoritative for asset metadata, aliases, watchlists, and ordering. Schema changes use Alembic. Reads tolerate an empty profile. Writes fail closed on incompatible profile versions, lock contention, invalid identifiers, duplicate names, or ambiguous asset references.

An opened profile is owned by the desktop window/session that successfully opened it. Profile ownership must live at the persistent desktop broker boundary rather than in a per-request Python sidecar because the sidecar process is short-lived. A second OSCA window or process must not acquire the same profile while the first window holds ownership. It may not mutate watchlists, recent assets, or any other profile-scoped state through that profile.

Selecting a profile is only a preference operation and does not grant mutation authority. Profile-scoped mutations require the requesting desktop window to own that profile. Closing the owning window or explicitly leaving its opened profile releases ownership. A failed concurrent open or mutation must not change the first window's active profile, persisted watchlists, member ordering, recents, or profile metadata.

Global remembered-profile preferences may be updated for future launches, but they must not silently replace the active profile context of another already-open desktop window.

The lifetime session lease is also an inter-process safety boundary for supported non-UI mutations. A direct Python/CLI desktop-API mutation must acquire the same profile session lease before mutating and therefore must fail closed while a desktop window owns that profile. Broker-launched short-lived sidecars are authorized only for the exact profile already owned by the requesting window; that broker ownership context allows them to reuse the lifetime lease while the existing Python mutation lock continues to serialize the actual write. The authorization is profile-specific and must not allow a sidecar to mutate any other profile.

Broker-level ownership conflicts are domain failures, not sidecar availability failures. The desktop client must surface them as a typed `profile_locked`/profile-ownership error with clear visible wording. `sidecar_unavailable` is reserved for failures to start, reach, or complete the sidecar request path itself.

## 7. Desktop application API

Python exposes typed request/response methods for:

- `asset.catalog.search`;
- `asset.catalog.detail`;
- `asset.catalog.register`;
- `watchlist.list`;
- `watchlist.create`;
- `watchlist.update`;
- `watchlist.delete`;
- `watchlist.membership.set`;
- `watchlist.reorder`.

React accesses these methods only through the existing `desktop_request` bridge. Rust gains no generic database, filesystem, network, or secret authority. The Rust broker may enforce window/session ownership and lifetime locking needed to preserve the Python-authoritative profile safety contract across short-lived sidecar requests. Python remains authoritative for profile-scoped validation and persistence, including direct supported non-UI desktop-API mutations.

## 8. Desktop UX

D4 adds a first-class Markets area with:

- search and filter controls;
- result list with canonical identity and local availability;
- asset detail panel;
- recent assets for the opened profile;
- watchlist sidebar and membership controls;
- rename and ordered member controls;
- empty, loading, error, ambiguity, locked-profile, and ownership-conflict states;
- keyboard navigation, visible focus, reduced-motion, forced-colors, and narrow-layout support.

## 9. Performance budgets

On a catalog of 50,000 assets and 100 watchlists:

- normalized local search p95 is at most 150 ms after database open;
- first result page returns at most 100 items;
- watchlist mutation p95 is at most 250 ms excluding lock wait;
- UI remains responsive through pagination or virtualization.

## 10. Safety and non-goals

D4 does not add streaming quotes, charting, quantitative analysis, recommendation ranking, alerts, portfolio ownership, brokerage connections, or order execution. Provider enrichment must reuse D3 policy and explicit network-consent boundaries.

## 11. Exit criteria

- Requirements and OpenSpec validation pass.
- Unit, integration, migration, desktop API, frontend, broker, architecture, and persistence tests pass.
- Regression tests prove one window cannot take over or mutate another window's opened profile and that ownership is released when the owning window closes/leaves the profile.
- Regression tests prove a supported direct Python/CLI mutation cannot bypass a desktop-held session lease, while a broker-authorized sidecar can still mutate only its owning window's leased profile without deadlocking.
- Regression tests prove broker profile-ownership conflicts are surfaced as typed profile-lock errors rather than `sidecar_unavailable`.
- Clean-profile manual acceptance passes on macOS ARM64 and Linux x86-64.
- Large-catalog performance evidence is retained.
- Accessibility, recovery, ambiguity, profile-lock, and per-window ownership behavior pass.
- Traceability and exit review are reconciled before owner-directed merge.
