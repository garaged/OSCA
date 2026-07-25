# M4 Implementation Notes

- The first M4 slice is additive and introduces a new `osca.research` package.
- Market-data contracts from M2 and M3 are not modified.
- Graph validation is intentionally pure and deterministic.
- Visualization contracts reference analytical output identities, not storage internals.
- Application services cover ad hoc promotion, hypothesis state transitions, deterministic timeline ordering, graph planning, evidence-report assembly, and dashboard composition.
- M4 remains persistence-free so later interface and extension milestones can reuse the same internal contracts without changing their meaning.
