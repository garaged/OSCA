# D4 Manual Acceptance

Run on macOS ARM64 and Linux x86-64 using an isolated clean profile.

1. Launch and verify Markets is keyboard reachable with permanent research/no-execution boundaries.
2. Search AAPL, Apple, BTC, XBTUSD, and ABC. Confirm deterministic ordering and explicit ambiguity for ABC.
3. Filter and inspect canonical ID, venue, class, currency, aliases, provenance, and local-data status.
4. Create, rename, delete, and recreate watchlists. Confirm duplicate names fail clearly.
5. Add assets, reject duplicate membership, remove assets, reorder members, restart, and verify persistence.
6. Open the same profile concurrently and confirm mutation locking fails closed without corruption.
7. Verify no network traffic during catalog, detail, recent-asset, or watchlist operations.
8. Validate light/dark/high contrast, reduced motion, VoiceOver/Orca, 320px/680px/desktop widths.
9. Build native packages and smoke the packaged app with persisted watchlists.

Record environment, screenshots, network observation, profile identifiers, and exact failures without committing private host paths.
