# D8 Validation Evidence — Virtual-Portfolio Accounting Foundation

## Accepted baseline

- PR: #88
- PR head accepted: `620e8c9cdae188ca55945689c849b73e743c008a`
- Manual acceptance: completed by the user
- Supported-platform coverage: macOS ARM64 and Linux x86-64

## Hosted validation

Exact-head hosted validation passed on `620e8c9cdae188ca55945689c849b73e743c008a`.

Quality run #1183:

- OpenSpec: success
- secret scan: success
- python-and-architecture: success
- contributor rehearsal (macOS ARM64): success
- contributor rehearsal (Linux x86-64): success
- package lifecycle (macOS ARM64): success
- package lifecycle (Linux x86-64): success

Desktop Foundation run #319:

- python-desktop-api: success
- frontend: success
- rust-broker: success
- linux-x86_64 desktop package smoke: success

The Python/architecture gate included Ruff, strict mypy, tests/contracts/migrations/links/architecture validation, and trusted-local extension conformance. The desktop API gate included boundary Ruff/mypy, launcher/API tests, and bundled-sample verification.

## Manual acceptance outcome

The D8 procedure passed in full on the supported platforms, including:

- independent virtual-portfolio identity, balances, revisions, journals, and state;
- Decimal-safe acquisition/accounting evidence and balanced journal postings;
- multiple open lots with fail-closed ambiguous disposal and explicit retained-lot allocation;
- dividends/distributions, splits, forks, and explicit book-cost transfer evidence;
- multi-currency cash/FX behavior and degraded valuation when price/FX evidence is incomplete;
- append-only compensating reversals without destructive history mutation;
- clone/reset lineage with source portfolio left unchanged;
- digest-protected portable export and atomic restore/conflict rejection;
- explicit valuation provenance, missing-evidence disclosure, and recovery after local valuation evidence is supplied;
- immutable analytics snapshots, cumulative performance, and drawdown evidence;
- current per-asset attribution with provenance;
- non-mutating hypothetical asset/FX scenarios;
- descriptive benchmark comparison without recommendation language;
- profile ownership/isolation for writes and read-only analytical behavior;
- responsive, keyboard, focus, degraded-state, table-overflow, reduced-motion, and forced-color accessibility checks;
- continued research-only boundaries: no recommendations, broker/exchange connection, live orders, real-capital operation, arbitrary user-code execution, mandatory paid provider dependency, or fabricated missing evidence.

## Acceptance findings resolved before final pass

Manual testing surfaced two UI issues before final acceptance:

1. Portfolio creation/selection state was not synchronized into the Accounting operations and lifecycle / analytics surfaces, hiding the disposal controls until remount. D8 now synchronizes portfolio workspace changes across all three Portfolio Lab sections.
2. The accounting-operation disclosure grid stretched collapsed operations to the height of the open card. The final UI uses a compact disclosure layout with the active operation spanning the row and responsive single-column fallback.

Both fixes are included in the accepted head and covered by frontend source-contract tests. The final manual pass reported all D8 tests passing.
