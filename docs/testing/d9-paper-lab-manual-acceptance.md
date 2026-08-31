# D9 Paper Lab Manual Acceptance Runbook

This runbook validates D9 Forward Paper Evaluation and Simulated Orders through the desktop product surface. It is acceptance evidence, not a trading guide. All orders are simulated research evidence only.

## Acceptance classification

This is not a twenty-section mandatory regression script. The exact-head automated suite is authoritative for deterministic fill arithmetic, order lifecycle, risk rejection, replay/idempotency, persistence, protocol boundaries, and source restrictions. The reviewer performs the **required human path** below on each supported platform, then adds only the **exploratory probes** whose triggers apply.

| Coverage | D9 cases | Evidence source |
|---|---|---|
| Automated | Draft versioning, eligibility, market/limit/stop/scheduled fills, partial fills, fees/latency, calendar behavior, cancellation, risk gates, retained controls, explicit lots, checkpoint/recovery, comparison, ownership, source boundaries | `tests/paper/test_forward_*.py`, `tests/test_d9_desktop_*.py`, frontend and Rust broker tests, hosted Quality/Desktop Foundation |
| Required human path | Paper Lab discoverability, simulated-only disclosure, account/run/draft/fill feedback, provenance readability, D8 effect visibility, keyboard/focus, zoom/narrow width, contrast/status meaning | Sections 0--4 and 19--20 below |
| Exploratory | restart/recovery, second-process ownership, package smoke, an order type or risk/degraded path materially changed by the PR, platform-specific rendering defect | Sections 5--18, only when triggered below |

Record the exact head and automated gate results once. Do not repeat a deterministic case manually merely because it appears in an older runbook.

## Supported acceptance platforms

Run the complete acceptance flow on:

- macOS ARM64;
- Linux x86-64.

Use a disposable OSCA profile and local/synthetic governed evidence. Do not configure brokerage or exchange credentials.

## Required human path

### 0. Automated baseline, build and launch

From a clean checkout of the exact PR head:

```bash
make acceptance-check
make acceptance-seed
```

Launch the desktop app using the repository's documented desktop launcher. In Workspace, create or open a disposable validated profile and keep that window as the profile owner.

Expected:

- the app opens normally;
- `Paper Lab` appears as a first-class desktop area;
- no broker, exchange, or credential setup is required;
- the Paper Lab header prominently states `SIMULATED ONLY` and that no real-capital path exists.

### 1. Prepare a D8 virtual portfolio

1. Open `Portfolio Lab`.
2. Create a portfolio named `D9 Manual Acceptance`.
3. Use base currency `USD` and starting cash `10000`.
4. Return to `Paper Lab`.
5. Select that portfolio in `Run, retained account and execution assumptions`.

Expected:

- Paper Lab lists the D8 portfolio;
- D9 does not create a second cash balance or paper-only portfolio ledger;
- later fills must alter this D8 portfolio through normal accounting events.

### 2. Create/select the retained M8 paper account and retain a run

Paper Lab must use a retained M8 `PaperAccount` control identity. It must not synthesize an arbitrary paper-account UUID for a run.

1. In `New paper account name`, enter `D9 Manual Acceptance Paper`.
2. Select `Create retained paper account`.
3. Confirm the new account is selected under `Retained M8 paper account` and shows base currency `USD` and status `active`.
4. Record its paper-account UUID with your acceptance notes.
5. Select `Allow simulation` and confirm the displayed retained control becomes `allow`.
6. Keep the generated paper-run and assumption UUIDs.
7. Start execution assumptions with:
   - spread: `0` bps;
   - slippage: `0` bps;
   - fee: `0` bps;
   - flat fee: `0`;
   - latency: `0` ms;
   - max volume participation: `1`;
   - optional notional limits empty.
8. Select `Retain run + assumptions`.

Expected:

- the account exists as retained M8 paper metadata and remains selectable after a refresh/restart;
- its control decision is retained separately from D8 balances;
- success feedback appears;
- run inspection becomes available;
- the retained D8 cash remains `USD 10000`;
- the paper-account record does not duplicate cash, positions, lots, P&L, or fees;
- no network/provider activity is required.

### 3. Confirm one draft and inspect the visible safety/evidence feedback

Create a market-buy draft using:

- instrument: `equity:XNAS:AAPL`;
- timeframe: `1h`;
- currency: `USD`;
- keep the generated dataset-revision UUID;
- side: `Buy`;
- type: `Market`;
- quantity: `10`.

Select `Retain draft v1`.

Expected before confirmation:

- the draft is retained;
- `Retained order lifecycle and fills` still shows no confirmed order;
- the message states the draft is not active until explicitly confirmed.

Now select `New draft version`, alter quantity to `11`, retain v2, then restore quantity to `10` and retain a later version if desired.

Expected:

- versions are immutable retained evidence;
- editing does not overwrite a previously retained version.

Select the desired retained version and choose `Confirm SIMULATED-ONLY order`.

Expected:

- a confirmed simulated order appears;
- confirmation is a separate action from draft retention;
- confirmation uses the retained paper-account control decision rather than caller-provided pause/kill booleans;
- no venue, account number, API token, broker, exchange, or external destination is requested;
- lifecycle begins with explicit confirmation and risk evidence.

### 4. Process one eligible local bar and inspect the D8 accounting effect

Immediately after confirmation, inspect the current bar timestamps in `Governed completed-bar evidence`.

First, deliberately set a bar start earlier than the order's displayed `Eligible` timestamp and process it.

Expected:

- no fill occurs;
- retained lifecycle/accounting does not fabricate an execution from an ineligible bar.

Next select `New bar identity` **after confirmation**. The new bar must inherit:

- the draft instrument;
- the draft timeframe;
- the draft dataset-revision UUID.

Set a complete bar such as:

- open `100`;
- high `102`;
- low `99`;
- close `101`;
- volume `1000`;
- session open checked.

Ensure the new bar starts at or after eligibility, then process it.

Expected:

- the market order fills deterministically from the eligible bar;
- fill evidence shows quantity, execution price, fee, bar evidence ID, dataset revision, and assumption ID;
- D8 accounting revision advances once;
- position quantity is reflected in the linked D8 portfolio.

## Exploratory probes — run only when triggered

Run a probe when the PR changes that behavior, a defect/regression indicates the risk, a migration/recovery/package change occurred, or a supported platform renders it materially differently. Otherwise cite the automated evidence in the acceptance record.

### 5. Replay the same governed bar

Without changing the bar evidence UUID, process the same bar again. Refresh run inspection, then restart the desktop app and inspect the same paper run again if the UI retains the run IDs in your test notes.

Expected:

- the retained fill is replayed idempotently;
- no second fill is added;
- no duplicate D8 acquisition event is created;
- position/cash/revision do not duplicate the economic effect.

This validates the terminal-order replay behavior as well as restart-safe reconciliation.

## 6. Completed-bar valuation mark and degraded evidence

With the acquired position still open, choose `Retain close as valuation mark` for the completed bar.

Expected:

- the bar close is retained as separate valuation evidence, not treated as the fill price;
- portfolio equity/unrealized P&L become available when required evidence is complete;
- provenance identifies the paper bar source and dataset/bar revision.

Then create a new bar identity but uncheck `Complete bar` and attempt to retain its close as a mark.

Expected:

- the mark is rejected;
- incomplete evidence never becomes valuation authority.

For any non-base-currency scenario, omit required FX evidence and confirm valuation degrades/fails closed instead of inventing a conversion.

## 7. Deterministic partial fills and liquidity evidence

Start a fresh simulated run against a fresh D8 portfolio or reset test state. Reuse/select a retained active paper account and retain assumptions with:

- max volume participation `0.10`;
- volume required;
- zero spread/slippage/fees for easier arithmetic.

Create and confirm a market-buy order for quantity `20`. Generate an eligible bar with volume `50`.

Expected:

- at most `5` units fill from that bar;
- order status becomes partially filled;
- remaining quantity is retained.

Generate a later governed bar with sufficient volume and process it.

Expected:

- later fill sequence is deterministic;
- total fills never exceed original quantity;
- once fully filled, subsequent unseen bars produce a terminal no-op.

Now repeat with volume omitted while `require_volume` is true.

Expected:

- fill blocks rather than assuming unlimited liquidity.

## 8. Spread, slippage, fees, and latency

Use a fresh run and assumptions containing visible non-zero values, for example:

- spread `5` bps;
- slippage `10` bps;
- fee `20` bps;
- flat fee `1.25`;
- latency `1500` ms.

Create and confirm a small buy order and process an eligible complete bar.

Expected:

- eligibility includes latency;
- execution price reflects adverse spread/slippage, not a favorable hidden adjustment;
- retained fee reflects both percentage and flat-fee assumptions;
- the fill points to the exact retained assumption ID.

## 9. Limit-order semantics

Use a fresh run/order.

### Buy limit

Set type `Limit`, quantity `10`, limit price `100`.

Exercise two bars:

1. favorable gap open below the limit while trading through the limit range;
2. a bar where adverse spread/slippage would push the computed buy price above `100`.

Expected:

- the favorable opening gap may use the better open;
- the second case must not violate the buy limit after execution adjustments.

### Sell limit

Use an existing held position and explicit lot allocation when required. Confirm a sell limit and exercise a favorable opening gap above the limit.

Expected:

- favorable open may be used;
- execution never violates the sell limit in the unfavorable direction.

## 10. Stop-order gap semantics

Create a buy stop at `100`, then provide an eligible bar that gaps open at `105` and trades above the stop.

Expected:

- the stop does not optimistically fill at `100`;
- execution is based on the eligible gap/open plus adverse configured adjustments.

Repeat directionally for a sell stop if desired.

## 11. Scheduled market order

Create type `Scheduled market` and supply an ISO-8601 schedule in the future. Confirm the draft.

Process a bar before the scheduled time and then an eligible later bar.

Expected:

- pre-schedule bar never fills;
- later eligible bar can fill;
- schedule does not create background brokerage activity or an external order.

## 12. Session/calendar behavior

For `equity:XNAS:AAPL`, process an otherwise eligible bar with `Market session open` unchecked.

Expected:

- no fill occurs.

For a 24/7 crypto research case, use the accepted 24/7 policy/identity from the implementation test path and confirm it is evaluated separately rather than pretending an equity calendar applies to all assets.

## 13. Cancellation

Create and confirm an unfilled simulated order, then select `Cancel simulated order`.

Expected:

- lifecycle becomes cancelled;
- later bars do not fill it.

Repeat with a partially filled order.

Expected:

- already retained fills and D8 accounting remain intact;
- only the remaining quantity is cancelled;
- history is not rewritten.

## 14. Risk gates and retained paper-account controls

Exercise at least these portfolio/order risk cases:

- buy whose required simulated cash exceeds D8 cash;
- sell whose requested quantity exceeds held quantity;
- max order notional below requested order notional;
- max position notional below projected position notional.

Expected:

- each case rejects/fails closed with a retained reason;
- rejected fill does not mutate D8 accounting;
- no hidden margin/borrowing behavior appears.

Now validate the retained M8 control identity:

1. Retain a new draft but do not confirm it yet.
2. Select `Pause simulation` for the selected retained paper account.
3. Attempt `Confirm SIMULATED-ONLY order`.
4. Confirm the order is not activated and D8 accounting is unchanged.
5. Select `Allow simulation`, then confirm the same retained draft; confirmation should now succeed if its normal risk gates pass.
6. Before processing a later eligible bar, select `Engage simulated kill switch`.
7. Process the bar and confirm no fill/accounting mutation occurs.
8. Select `Allow simulation` again and process a later eligible bar.

Expected:

- pause and kill-switch decisions are retained paper-control evidence;
- confirmation and bar processing derive control state from that retained account server-side;
- blocked controls cannot be bypassed by renderer parameters;
- `Allow simulation` creates a later retained allow decision and permits only local simulated processing;
- no control decision can authorize a live/external order.

## 15. Explicit lot allocation on sell

Prepare a D8 portfolio with at least two open AAPL lots. In Paper Lab create a simulated sell that can be satisfied by more than one open lot.

First leave lot allocations empty.

Expected:

- D9 rejects ambiguous disposal rather than silently applying FIFO/LIFO/average cost.

Then enter allocations as comma-separated pairs:

```text
<lot-uuid-1>=<quantity>,<lot-uuid-2>=<quantity>
```

Confirm/process the sell.

Expected:

- retained fill carries explicit lot allocation;
- D8 disposal posts exactly once against those lots;
- realized P&L/book-cost evidence remains auditable.

## 16. Checkpoint and restart recovery

After processing a governed bar, select `Checkpoint this bar` twice without changing its evidence UUID.

Expected:

- the second request returns the same retained checkpoint;
- sequence is not duplicated.

Change checkpoint evidence while attempting to reuse the same idempotency key through the protocol test path.

Expected:

- conflict fails closed.

Restart OSCA and reopen the same profile/run.

Expected:

- the retained paper account and latest control decision remain selectable/inspectable;
- retained orders/fills/lifecycle/checkpoint remain available;
- already-posted fills are not duplicated;
- deterministic processing can continue from later evidence.

## 17. Forward vs. backtest comparison

In `Forward vs. backtest evidence`, provide:

- a retained D7 backtest result ID;
- the corresponding strategy version ID;
- separate backtest and forward evaluation windows;
- a comparable metric such as return;
- the D9 execution-assumption ID already shown by Paper Lab.

Select `Build descriptive comparison`.

Expected:

- output keeps D7 result ID and D9 run ID distinct;
- backtest and forward windows remain visibly separate;
- assumption identity and methodology differences remain explicit;
- metric delta is descriptive only;
- no wording suggests buy/sell/hold advice or a recommendation-to-order action.

## 18. Profile ownership and isolation

With the original profile open/owned in the first OSCA window/process, attempt a D9 write from another window/process where supported, including a paper-account/control mutation.

Expected:

- mutation is blocked by profile ownership;
- the first owner's retained state is not corrupted;
- `paper.account.list` and `paper.run.inspect` remain bounded research reads when the product/session boundary permits them.

Release the original owner, then reopen from the other process and repeat a safe mutation.

Expected:

- ownership transfers only after release.

Open a clean second profile.

Expected:

- no retained paper-account/control/run/order/fill/accounting evidence leaks across profiles.

## Required completion review

### 19. Accessibility and responsive review

Validate Paper Lab with keyboard only:

- traverse navigation, retained-account creation/selection, allow/pause/kill-switch controls, forms, confirmation, order selection, cancellation, bar controls, checkpoint and comparison;
- focus is visibly indicated;
- all controls remain operable without pointer input.

Validate at narrow desktop width and at increased text/zoom.

Expected:

- grid collapses without horizontal product-layout breakage;
- long UUIDs and evidence text wrap/scroll safely;
- 44 px minimum interactive targets remain usable.

Validate high-contrast/forced-colors where supported and reduced-motion preference.

Expected:

- selected/error/safety/lifecycle meaning does not rely solely on color;
- focus remains visible;
- no required animation remains.

### 20. Universal safety boundary

Before signing off, inspect the rendered Paper Lab and source/product behavior for all of the following.

Must remain absent:

- broker or exchange destination selection;
- broker/exchange credentials;
- live-order API calls;
- real-capital action;
- autonomous live execution;
- recommendation-to-order shortcut;
- arbitrary user code execution;
- silent provider/network fetch from Paper Lab;
- paid-provider requirement for the local/synthetic acceptance flow.

Must remain explicit:

- `SIMULATED ONLY`;
- retained paper-account/control identity;
- local/governed evidence identity;
- execution assumptions;
- lifecycle/fill/accounting provenance;
- descriptive-only comparison language.

## Recording results

For each supported platform, record:

- exact D9 commit SHA;
- OS/architecture;
- package/app build used;
- automated baseline result and required human-path PASS/FAIL;
- exploratory sections exercised, including their trigger, or explicitly waived as covered by the named automated gate;
- any screenshots/logs retained locally as evidence;
- accepted limitations or defects discovered.

Do not mark D9 complete or merge PR #89 until both supported-platform manual acceptance and exact-head hosted CI are green and `docs/milestones/d9/validation-evidence.md` plus `exit-review.md` are updated.
