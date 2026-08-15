# D8 Manual Acceptance — Virtual-Portfolio Accounting Foundation

## Preconditions

- Use a disposable clean profile.
- Use bundled/local/synthetic data only.
- Do not configure broker/exchange credentials or real-capital accounts.
- Complete automated baseline and hosted CI before final acceptance.

## Acceptance flow

1. Create two virtual portfolios with different names and starting cash; confirm identity/base currency/state are independent.
2. In the first portfolio, record a simulated acquisition, fee, dividend, and disposal using a single unambiguous lot.
3. Inspect journal evidence and confirm every transaction is balanced and traceable to its economic event.
4. Create a second acquisition lot, attempt an ambiguous disposal without allocation, and confirm the operation fails closed; then provide explicit lot allocation and confirm success.
5. Record a split and retry the same source identity; confirm it is applied once only.
6. Add valuation evidence and inspect cash, positions, lots, book cost, realized/unrealized P&L, income, fees, exposure, allocation, equity, and provenance.
7. Remove/omit required valuation evidence for another asset/currency and confirm the result is visibly degraded rather than fabricated.
8. Clone the portfolio, then reset it. Confirm new identities/lineage and that the source journal remains unchanged.
9. Export a portfolio bundle, restore it into an isolated clean profile, and confirm deterministic replay/projection. Tamper with a copy and confirm restore rejects it without partial mutation.
10. Restart the desktop app and reopen the profile; confirm portfolio/accounting state persists.
11. Attempt to open the same profile from a competing process/window where supported and confirm mutation ownership remains enforced.
12. Confirm the UI and System boundaries still report no recommendations, no broker connections, no autonomous execution, no live orders, and no real-capital path.

## Platform coverage

Final D8 acceptance should cover macOS ARM64 and Linux x86-64, matching the supported desktop coverage established by D7.

## Evidence recording

Record exact commit, package/platform, automated commands, hosted checks, manual PASS/FAIL per step, and any accepted limitations in `validation-evidence.md`. Do not mark `exit-review.md` complete before this evidence exists.
