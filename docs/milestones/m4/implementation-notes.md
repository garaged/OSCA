# M4 Implementation Notes

- The first M4 slice is additive and introduces a new `osca.research` package.
- Market-data contracts from M2 and M3 are not modified.
- Graph validation is intentionally pure and deterministic.
- Visualization contracts reference analytical output identities, not storage internals.
- The current tests are unit-level contract tests; application services and component tests will follow in later M4 slices.
