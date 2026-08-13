# D4 Manual Acceptance

Run on macOS ARM64 and Linux x86-64 using an isolated clean profile.

1. Launch and verify Markets is keyboard reachable with permanent research/no-execution boundaries.
2. Search AAPL, Apple, BTC, XBTUSD, and ABC. Confirm deterministic ordering and explicit ambiguity for ABC.
3. Filter and inspect canonical ID, venue, class, currency, aliases, provenance, local-data status, and recent-assets behavior.
4. Create, rename, delete, and recreate watchlists. Confirm duplicate names fail clearly.
5. Add assets, reject duplicate membership, remove assets, reorder members, restart, and verify persistence.
6. With window A holding profile A open, open a second OSCA window/process and attempt to open profile A. Confirm the second open fails closed as `profile_locked` (or equivalent visible profile-in-use wording), not `sidecar_unavailable`; window A remains on profile A and no watchlist/recent/profile state changes.
7. In the second window, merely selecting profile A must not grant mutation authority. Attempt a watchlist/recent-asset mutation and confirm it fails closed as a profile ownership/lock error, not as sidecar unavailability, while window A continues to mutate normally.
8. While window A still owns profile A, submit a supported direct Python/CLI desktop-API mutation for profile A, for example `watchlist.create`. Confirm it fails closed with `profile_locked`/profile-in-use wording, does not create or change profile state, and window A remains healthy. Do not edit SQLite, Parquet, configuration, or lock files directly.
9. Close window A (or explicitly leave its opened profile), then repeat the supported direct Python/CLI mutation. Confirm it can now acquire the profile and succeeds; remove any temporary test watchlist afterward.
10. Open profile A from the second desktop window after the first owner releases it and confirm desktop ownership can now be acquired and normal mutations succeed.
11. Repeat with window A on profile A and window B on a different profile B. Confirm changing or opening B never silently changes A's active profile context.
12. Verify no network traffic during catalog, detail, recent-asset, or watchlist operations.
13. Validate light/dark/high contrast, reduced motion, VoiceOver/Orca, 320px/680px/desktop widths.
14. Build native packages with the canonical repository build. Launch the generated packaged application directly with no development server, `make run`, manually started Python process, or repository-local Python environment running. Confirm the bundled desktop sidecar starts automatically, persisted watchlists are usable, and the same profile-ownership checks pass. A packaged application that reports `sidecar_unavailable`, exits its sidecar, or requires a separately started service fails this gate.

For the concurrency checks, record which window owns each profile, the exact rejected action/error, and confirm the first owner's watchlists, ordering, recent assets, and selected profile remain unchanged.

For the supported non-UI check, use the versioned desktop API (`uv run python -m osca.desktop_api.stdio`) rather than direct file/database edits. The required invariant is: desktop-owned profile + external supported mutation => rejected; no desktop owner + supported mutation => allowed.

For the packaged-app check, validate the actual generated bundle rather than Tauri development mode. The packaged application must be self-contained for its desktop service on the supported platform.

Record environment, screenshots, network observation, profile identifiers, and exact failures without committing private host paths.
