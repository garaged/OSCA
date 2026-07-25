# M5 Intent - Independent Extension Packaging and Activation

- **Status:** Active
- **Baseline:** M4 complete
- **Last reviewed:** 2026-07-24

## Intent

Enable OSCA to accept independently packaged extension metadata through governed contracts, validate compatibility and declared access, create exact installation records, make activation an explicit trust decision, and preview impacts before disable or uninstall.

M5 turns the M4 extension-compatible boundary into an inspectable package lifecycle foundation without executing untrusted code or building a public registry.

## Outcome

A local owner can evaluate an extension package manifest, see its category, compatibility, schemas, permissions, integrity, trust tier, dependencies, and impacted retained artifacts, then produce an installation or activation decision with reproducibility-safe records.

## Non-goals

- Running third-party extension code.
- Public extension registry operation.
- Cryptographic signature implementation beyond typed integrity/signature metadata.
- Strategy/backtest execution.
- ML model training or LLM tool orchestration.
- Live trading.
