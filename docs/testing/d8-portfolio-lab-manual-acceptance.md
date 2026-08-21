# D8 Portfolio Lab Manual Acceptance

Use this checklist only after the D8 branch has passed hosted automated validation. Run it on each supported desktop platform from a clean or disposable OSCA profile. Keep the workflow local/synthetic: D8 must not require a paid provider, broker account, live order path, or real capital.

## Preconditions

- Build and launch the D8 desktop application from the candidate branch/package.
- Create or open a disposable OSCA profile and keep that window as the profile owner.
- Have a second disposable profile available for export/restore testing.
- Use exact decimal text for monetary/quantity values.
- Do not enter credentials or connect a broker/exchange; no such connection is required by D8.

## 1. Portfolio creation and isolation

1. Open **Portfolio Lab** from the desktop navigation.
2. Confirm the page identifies itself as simulated accounting and visibly states the append-only/local/no-real-capital boundaries.
3. Create `Portfolio A` with base currency USD and starting cash `10000.01`.
4. Create `Portfolio B` with starting cash `2500`.
5. Switch between the two portfolios.
6. Confirm **Accounting operations and lifecycle** and **Performance, attribution and scenarios** automatically follow the selected/newly created portfolio without leaving Portfolio Lab or manually refreshing it.

Pass when each portfolio retains an independent identity, starting balance, revision, journal, and state. No value from one portfolio should appear in the other, and all Portfolio Lab sections stay synchronized to the current portfolio.

## 2. Acquisition, cash, positions, lots, and journal

1. Select `Portfolio A`.
2. Record a simulated acquisition for an instrument such as `equity:XNAS:AAPL`: quantity `5`, unit price `100`, fee `1`.
3. Inspect cash, positions, open lots, and immutable journal evidence.

Pass when cash decreases by `501`, the position quantity is `5`, book cost is `501`, the fee is retained, and the acquisition has balanced debit/credit evidence. No broker/order/execution affordance should appear.

## 3. Multiple lots and explicit disposal allocation

1. Add a second acquisition of the same instrument at a different price so two open lots can satisfy a disposal.
2. In **Accounting operations and lifecycle → Simulated disposal**, confirm **Lot allocation** defaults to **No explicit lot — exercise fail-closed allocation**.
3. Leave that value selected and submit a quantity that either open lot could satisfy.
4. Confirm the operation fails closed with an explicit-lot requirement and does not mutate the portfolio.
5. Select one retained lot explicitly and repeat the disposal.

Pass when ambiguous disposal is rejected, the selected lot is reduced exactly, cash/proceeds/fees/realized P&L update consistently, and no implicit FIFO/LIFO/tax-accounting policy is invented.

## 4. Corporate actions

Use the accounting-operations panel to exercise these independently:

- record a dividend/distribution;
- apply a split to a held position;
- for a fork/distribution, create a new instrument and, when allocating non-zero book cost, choose the source lot explicitly.

Pass when each action is represented by retained economic evidence and balanced journal entries, a repeated source identity cannot apply the same economic action twice, split quantity changes without changing total book cost, and fork book-cost transfer remains explicit.

## 5. FX and multi-currency valuation

1. Journal an FX cash conversion from USD to another currency such as EUR.
2. Create/hold an instrument whose book currency matches that non-base currency.
3. Record local valuation evidence for the instrument.
4. Observe valuation state before complete FX-to-base evidence exists.

Pass when the portfolio shows a degraded/missing-evidence state rather than inventing base-currency equity or P&L. Once complete price/FX evidence is supplied through the supported evidence path, the projection should recover and preserve source/effective-time provenance.

## 6. Corrections are append-only

1. Choose a non-opening economic event in **Correction reversal**.
2. Enter a reason and append the reversal.
3. Reinspect events and journal evidence.

Pass when the original event remains visible, a compensating reversal is added, balances/lots reflect the corrected state, and direct historical mutation/deletion is not offered.

## 7. Clone and reset

1. Clone the current portfolio revision.
2. Confirm the clone is independently selectable and preserves source-portfolio/source-revision lineage.
3. Create a reset successor with a fresh starting-cash amount.
4. Return to the original portfolio.

Pass when clone/reset create new portfolio identities and never erase or rewrite the source journal. The original portfolio must be byte-for-byte unaffected at the product level: same economic events, journal evidence, balances, and lots.

## 8. Portable export and atomic restore

1. Prepare a portable bundle from `Portfolio A`.
2. Confirm the UI reports the output path and that provider payloads are not embedded.
3. Open/own the second disposable profile.
4. Restore the bundle by its path.
5. Compare restored identity, balances, positions, lots, journal, and valuation provenance with the source.
6. Attempt to restore the same identity again.

Pass when restore validates before mutation, reconstructs the retained portfolio authority, fails closed on conflicting identity, and does not leave a partially restored duplicate. The source profile must remain unchanged.

## 9. Valuation provenance and degraded state

1. Hold at least one instrument without a complete valuation observation.
2. Confirm Portfolio Lab lists the missing evidence and does not fabricate equity/unrealized P&L/exposure.
3. Record a local valuation observation with source ID/effective time/revision.
4. Reinspect **Valuation provenance**.

Pass when missing evidence is explicit, retained observations show source/effective-time/revision, and complete evidence removes only the corresponding degraded condition.

## 10. Analytics snapshots, performance, and drawdown

1. With complete valuation evidence, select the portfolio in **Performance, attribution and scenarios**.
2. Capture an analytics snapshot.
3. Change only retained valuation evidence, then capture at least one more snapshot.
4. Inspect the performance table, cumulative return, and max drawdown.

Pass when snapshots are retained as immutable derived evidence, performance is computed from captured portfolio equity rather than reconstructed from current holdings, and incomplete valuation state prevents snapshot capture.

## 11. Attribution

Inspect **Current per-asset attribution** after complete valuation evidence exists.

Pass when each held asset shows market value, book cost, unrealized P&L, allocation, and price provenance. Non-base-currency assets must also retain FX provenance or show degraded state.

## 12. Hypothetical scenario

1. Enter a decimal asset shock such as `0.10` for a held instrument.
2. Optionally enter an FX shock for a non-base currency.
3. Run the scenario.
4. Reopen/reload the portfolio after the scenario.

Pass when baseline/scenario equity and equity change are displayed, the result explicitly says the portfolio was not mutated, and balances/lots/journal remain unchanged.

## 13. Descriptive benchmark comparison

1. Capture at least two analytics snapshots or otherwise establish a performance evidence window.
2. Enter local benchmark start/end values and a source ID.
3. Run the comparison.

Pass when portfolio return, benchmark return, and difference are displayed for the same evidence window, source provenance is retained, and the UI labels the comparison descriptive only. It must not recommend buying, selling, rebalancing, or changing strategy.

## 14. Profile ownership and isolation

1. While the first OSCA window owns the profile, attempt a D8 write from another window/process against the same profile where supported.
2. Confirm the second writer is rejected.
3. Release/close the first owner, then retry from the second window.
4. Repeat a read-only analytics report/scenario against a non-owned profile where the desktop architecture permits read access.

Pass when write ownership follows the existing broker-level profile lease, Python mutation locking adds defense in depth, and read-only analytical methods do not silently obtain mutation authority.

## 15. Responsive and accessibility review

At narrow and normal desktop widths, and with keyboard-only navigation:

- traverse Portfolio Lab, operations, details/summary controls, forms, tables, and analytics;
- confirm visible focus;
- confirm selected portfolio state is not conveyed only by color;
- confirm degraded state has text in addition to styling;
- confirm wide tables scroll horizontally rather than clipping content;
- check increased text size / zoom;
- where available, enable reduced-motion and forced-colors/high-contrast preferences.

Pass when controls remain operable/readable, focus is visible, evidence tables remain inspectable, and no safety/degraded-state meaning depends only on color, animation, or pointer hover.

## 16. Final boundary check

Before accepting D8, verify there is still no:

- investment recommendation or personalized buy/sell instruction;
- broker/exchange connection or live-order submission;
- real-capital operation;
- arbitrary user-code execution;
- mandatory paid provider dependency;
- silent mutation of accounting history;
- silent fallback that invents missing price or FX evidence.

Record platform, package/commit, profile paths used, any screenshots/logs retained as evidence, and PASS/FAIL for each section in `docs/milestones/d8/validation-evidence.md` during the final acceptance pass.