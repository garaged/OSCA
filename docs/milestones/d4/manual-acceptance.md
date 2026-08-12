# D4 Manual Acceptance

Run on macOS ARM64 and Linux x86-64 using an isolated clean profile.

1. Launch and verify Markets is keyboard reachable with permanent research/no-execution boundaries.
2. Search AAPL, Apple, BTC, XBTUSD, and ABC. Confirm deterministic ordering and explicit ambiguity for ABC.
3. Filter and inspect canonical ID, venue, class, currency, aliases, provenance, local-data status, and recent-assets behavior.
4. Create, rename, delete, and recreate watchlists. Confirm duplicate names fail clearly.
5. Add assets, reject duplicate membership, remove assets, reorder members, restart, and verify persistence.
6. With window A holding profile A open, open a second OSCA window/process and attempt to open profile A. Confirm the second open fails closed with a profile-in-use/ownership error, window A remains on profile A, and no watchlist/recent/profile state changes.
7. In the second window, merely selecting profile A must not grant mutation authority. Attempt a watchlist/recent-asset mutation and confirm it fails closed while window A continues to mutate normally.
8. Close window A (or explicitly leave its opened profile), then open profile A from the second window and confirm ownership can now be acquired and normal mutations succeed.
9. Repeat with window A on profile A and window B on a different profile B. Confirm changing or opening B never silently changes A's active profile context.
10. Verify no network traffic during catalog, detail, recent-asset, or watchlist operations.
11. Validate light/dark/high contrast, reduced motion, VoiceOver/Orca, 320px/680px/desktop widths.
12. Build native packages and smoke the packaged app with persisted watchlists and the same profile-ownership checks.

For the concurrency checks, record which window owns each profile, the exact rejected action/error, and confirm the first owner's watchlists, ordering, recent assets, and selected profile remain unchanged.

Record environment, screenshots, network observation, profile identifiers, and exact failures without committing private host paths.
