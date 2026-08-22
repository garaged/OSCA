# D9 Manual Acceptance — Forward Paper Evaluation and Simulated Orders

## Preconditions

- Use disposable profile state.
- Use local/synthetic governed bar data only.
- Use a D8 virtual portfolio with known starting cash.
- Do not configure broker/exchange credentials; D9 must not require or expose them.
- Complete automated validation and hosted CI before final acceptance.
- Execute the detailed [D9 Paper Lab manual acceptance runbook](../../testing/d9-paper-lab-manual-acceptance.md) on each supported platform.

## Acceptance flow

1. Create/select a retained M8 paper account, retain an explicit allow control, and bind the account/run to one D8 virtual portfolio; confirm balances remain owned by the portfolio rather than duplicated in paper state.
2. Create a simulated market-order draft. Edit it once and confirm a new immutable draft version is created.
3. Confirm one draft version and verify a prominent simulated-only warning; confirm no destination/venue/account credential is requested and confirmation derives the retained paper-account control server-side.
4. Step the run over local governed bars and verify a market order fills only from an eligible later bar, never from a bar that started before order eligibility.
5. Exercise a buy/sell limit order and verify favorable opening gaps use the open while fills never violate the limit price.
6. Exercise a stop order with a gap through the stop and verify the gap/open plus adverse execution assumptions are reflected rather than filling optimistically at the stop.
7. Configure bounded bar-volume participation and verify deterministic partial fills across bars. Remove required volume evidence and confirm filling blocks/degrades rather than assuming unlimited liquidity.
8. Inspect spread, slippage, fee, latency, liquidity, dataset/revision, calendar, retained control, and health-gate provenance on retained evidence.
9. For a session-bound equity order, verify closed-session bars do not fill. Exercise a 24/7 crypto policy separately.
10. Cancel an unfilled order and a partially filled order; verify retained fills remain accounted while only remaining quantity is cancelled.
11. Trigger risk failures such as insufficient cash/holdings or configured notional/exposure limit and verify the order/fill fails closed without accounting mutation.
12. Retain `pause` and `kill_switch` decisions on the selected paper account and confirm they block activation/processing without D8 mutation; retain a later `allow` decision and confirm only local simulated processing resumes.
13. For a sell spanning multiple D8 lots, omit lot allocation and confirm D9 blocks. Add explicit retained-lot allocation and confirm the fill posts exactly once into D8 accounting.
14. Restart after at least one fill/checkpoint. Recover the run and confirm the retained paper account/control, already-posted fills, and checkpoint survive without duplicate fills/accounting.
15. Exercise a scheduled market order and confirm it becomes eligible only at the scheduled/calendar-safe time; it must remain simulated and local.
16. Inspect forward-vs-backtest comparison evidence and confirm aligned assumptions/provenance are visible and wording remains descriptive only.
17. Attempt paper-account/control and order/run writes from a second process/window against an owned profile where supported; confirm profile ownership blocks mutation while bounded reads remain available where permitted.
18. Keyboard/zoom/narrow-width/high-contrast review of Paper Lab; confirm account/control, status, safety, rejection, degraded, and lifecycle meaning never depends only on color.
19. Final source/product boundary check: no broker/exchange destination, credentials, live-order API, real-capital action, autonomous live execution, recommendation-to-order shortcut, arbitrary code, or paid-provider dependency.

## Platform coverage

Final D9 acceptance should cover macOS ARM64 and Linux x86-64, matching D8 supported desktop coverage.

## Evidence recording

Record exact commit, platform/package, hosted checks, PASS/FAIL per runbook section, any accepted limitations, and manual findings in `validation-evidence.md`. Do not mark `exit-review.md` complete before the evidence exists.
