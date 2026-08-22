# OSCA Desktop User Guide

Status: Active end-user guidance for the desktop application through D9.

Audience: Users who want to perform market research and simulated evaluation without needing to understand OSCA's internal milestone structure or finance-specific implementation terminology.

OSCA is research and simulation software. It does not place live orders, connect to brokers for execution, or manage real capital.

## Start with the mental model

You do **not** need to use every menu section.

A useful way to think about the desktop application is:

1. **Workspace** — choose and own the local profile that contains your research state.
2. **Data Sources** — get or import governed data when the profile does not already contain what you need.
3. **Markets** — find assets and keep a short list of things you want to study.
4. **Workbench** — inspect the actual time series, charts, tables, ranges, and comparisons.
5. **Projects** — save a coherent research investigation so related evidence stays together.
6. **Strategy Lab** — define a rule-based strategy and test it on historical evidence.
7. **Portfolio Lab** — model cash, holdings, lots, transactions, valuation, and portfolio analytics.
8. **Paper Lab** — take a retained strategy/research idea forward through simulated orders using new governed evidence.

For most users the normal path is not "use the menu from left to right every time." Use only the areas required for the question you are trying to answer.

## Menu at a glance

| Area | Plain-language purpose | Use it when... | Usually comes after |
|---|---|---|---|
| **Workspace** | Manage the local research profile and application context. | Starting a session, switching profiles, checking ownership/health. | Nothing; start here. |
| **Markets** | Discover and organize assets of interest. | You know a ticker/asset or want to build a watchlist. | Workspace. |
| **Workbench** | Explore governed market data visually and numerically. | You want to inspect price history, ranges, charts, tables, or compare series. | Markets or Data Sources. |
| **Projects** | Group related research evidence and pinned artifacts. | A question is becoming more than a quick one-off inspection. | Workbench, Strategy Lab, or Portfolio Lab. |
| **Strategy Lab** | Define and backtest deterministic strategies. | You want to test "what would have happened if I followed these rules?" | Workbench/data readiness. |
| **Portfolio Lab** | Maintain a virtual portfolio and accounting evidence. | You want to model cash, holdings, lots, P&L, valuation, or scenarios. | Workspace; optionally Strategy Lab. |
| **Paper Lab** | Simulate future order behavior against governed forward evidence. | You want to evaluate a retained idea after historical backtesting, without real trading. | Portfolio Lab and usually Strategy Lab. |
| **Data Sources** | Inspect provider policy and import/acquire governed data. | Data is missing, stale, blocked, or you need to understand where it came from. | Workspace. |

## Workspace

### What it is

Workspace is the application-level starting point. A profile is the local boundary that owns configuration, retained evidence, portfolios, projects, paper state, and other research metadata.

### Use Workspace for

- creating, selecting, opening, or inspecting a profile;
- checking whether the profile is healthy and compatible;
- understanding which profile currently owns desktop mutations;
- changing to a clean profile for an independent experiment;
- recovering from profile or application-state problems.

### Recommended workflow

Open Workspace first, select the intended profile, and confirm it is healthy. Stay on one profile for a coherent research investigation. Use a separate disposable profile for experiments that should not share evidence.

### Common misunderstanding

A profile is **not** a trading account or portfolio. One profile can contain many projects, portfolios, datasets, strategies, and paper-evaluation runs.

## Markets

### What it is

Markets is the discovery and watchlist layer. It helps answer "what asset am I looking at?" before you start deeper analysis.

### Use Markets for

- finding an equity or cryptocurrency identity;
- selecting canonical asset identifiers rather than relying on ambiguous names;
- keeping watchlists or recent assets in the active profile;
- deciding which asset to open in Workbench.

### Recommended workflow

Search for the asset, verify the market/exchange or crypto identity, then open or carry that selection into Workbench. If data is unavailable, go to Data Sources rather than guessing or assuming the provider should have it.

### Common misunderstanding

Markets is primarily discovery and organization. It is not the main charting, backtesting, portfolio, or order-simulation area.

## Workbench

### What it is

Workbench is the primary analytical viewing area for governed market series. It is where you inspect what the data actually says before building more complex conclusions on top of it.

### Use Workbench for

- charts and table views of the same governed series;
- selecting ranges and inspecting exact observations;
- comparing available series;
- reviewing downsampling disclosure;
- exporting full-resolution evidence when supported;
- checking whether data is missing, incomplete, stale, or otherwise degraded.

### Recommended workflow

Start with a useful time range, inspect both chart and table, click or select important observations, and verify the data provenance. Use comparisons only when the second series is genuinely comparable. If the data looks wrong or unavailable, solve that in Data Sources before proceeding to Strategy Lab.

### Finance terms you may encounter

- **OHLC/OHLCV**: open, high, low, close, and optionally volume for each time interval.
- **Timeframe**: the duration represented by one bar, such as `1h` or `1d`.
- **Revision**: the retained identity of the exact dataset version being viewed.
- **Downsampling**: displaying fewer points for performance while retaining the full-resolution source separately.

## Projects

### What it is

Projects are research containers. They let you keep related evidence together instead of relying on memory or recreating a previous investigation.

### Use Projects for

- organizing a research question or thesis;
- pinning strategy definitions, backtests, charts, or other typed evidence;
- reopening an investigation after restarting OSCA;
- seeing when referenced evidence has become unavailable or degraded.

### Recommended workflow

Create a project when your investigation is worth returning to. Give it a name based on the question being studied, not just the ticker. Pin only evidence that materially supports the investigation.

Example: prefer `AAPL earnings trend study` over simply `AAPL`.

### Common misunderstanding

Projects do not duplicate provider datasets. They reference retained typed evidence and preserve the research relationship between artifacts.

## Strategy Lab

### What it is

Strategy Lab is for deterministic rule-based strategy definitions and historical backtesting.

The core question is: **"If these exact rules had been applied to this historical evidence, what would the simulated result have been?"**

### Use Strategy Lab for

- defining a supported strategy and parameters;
- selecting historical train/test or evaluation windows;
- running historical backtests;
- inspecting returns, drawdown, trades, assumptions, and warnings;
- bounded sensitivity analysis;
- walk-forward or out-of-sample evaluation;
- detecting fragile or overfit parameter choices.

### Recommended workflow

1. Verify the historical data in Workbench.
2. Define the strategy and retain its version.
3. Run a baseline backtest.
4. Inspect trades and assumptions, not only total return.
5. Run bounded sensitivity analysis.
6. Run walk-forward/out-of-sample evaluation.
7. Pin useful strategy/backtest evidence into a Project.
8. Only then consider a forward simulation in Paper Lab.

### Important terms

- **Backtest**: simulated application of rules to historical evidence.
- **Drawdown**: decline from a previous portfolio/equity peak.
- **Sensitivity analysis**: checking whether small parameter changes produce wildly different results.
- **Walk-forward/out-of-sample**: evaluating on evidence that was not used to select or tune the parameters.
- **Overfitting**: a strategy appears strong because it fits past data unusually well but may not generalize.

### Common misunderstanding

A profitable backtest is not a recommendation and is not proof that a strategy will work in the future.

## Portfolio Lab

### What it is

Portfolio Lab is the virtual accounting and portfolio-analysis area. Think of it as a research ledger: it models cash, holdings, lots, transactions, valuation evidence, P&L, and scenarios without real money.

### Main concepts

- **Portfolio**: one simulated collection of cash and holdings.
- **Position**: the total amount currently held in an instrument.
- **Lot**: a specific acquisition batch with its own quantity and book cost.
- **Book cost / cost basis**: retained accounting cost of an acquisition.
- **Realized P&L**: gain/loss recognized when holdings are disposed.
- **Unrealized P&L**: gain/loss implied by current valuation evidence for holdings not yet disposed.
- **Valuation observation**: evidence saying what an instrument or FX rate was worth at a stated time/source/revision.

### Use Portfolio Lab for

- creating multiple independent virtual portfolios;
- funding them with simulated starting cash;
- recording acquisitions and disposals;
- dividends, splits, forks, and FX conversions;
- explicit lot selection for disposals;
- reversing mistakes with compensating evidence rather than rewriting history;
- reviewing cash, holdings, book cost, P&L, exposure, performance, drawdown, attribution, and scenarios;
- cloning/resetting a portfolio while preserving lineage.

### Recommended workflow

Start with one simple base-currency portfolio. Record only a few acquisitions, add valuation observations, and learn how cash, positions, lots, and P&L relate before using multi-currency or corporate-action features.

For a disposal with multiple eligible lots, explicitly choose the lots. OSCA intentionally does not silently choose FIFO, LIFO, average cost, or a tax policy for you.

### Common misunderstanding

The acquisition price is historical accounting evidence. It is **not automatically a current market price**. Until a valuation observation exists, valuation-dependent figures may correctly show as unavailable.

## Paper Lab

### What it is

Paper Lab is forward simulated execution. It evaluates what a confirmed simulated order would do when later governed market evidence arrives.

It does **not** send orders to a broker or exchange.

### Prerequisite chain

Paper Lab is intentionally more structured because its evidence must be reproducible. The normal first-run sequence is:

1. Create/select a D8 virtual portfolio.
2. Create/select a retained paper account.
3. Retain an **Allow simulation** control decision.
4. Select the portfolio and retain the **paper run + execution assumptions**.
5. Create and retain a simulated-order draft.
6. Explicitly confirm the desired draft version.
7. Provide a later governed completed bar.
8. Process that bar through the simulator.
9. Inspect fill, lifecycle, risk, accounting, valuation, and checkpoint evidence.

If **Retain draft v#** is disabled, first confirm that **Retain run + assumptions** succeeded.

### Paper account versus portfolio

These are deliberately separate:

- the **paper account** controls whether local simulation is allowed, paused, or kill-switched;
- the **portfolio** owns cash, positions, lots, fees, P&L, and accounting.

The paper account does not have a second hidden cash balance.

### Execution assumptions

Paper simulation can retain assumptions such as spread, slippage, fees, latency, and maximum volume participation. These make simulated fills less unrealistically optimistic and ensure results can be reproduced.

### Order terms

- **Market order**: simulated order that can fill at an eligible market price subject to assumptions.
- **Limit order**: sets a price boundary that the simulated execution must not violate in the unfavorable direction.
- **Stop order**: activates after a stop condition; gaps can lead to fills worse than the stop price.
- **Scheduled market order**: becomes eligible only at/after the scheduled time.
- **Partial fill**: only part of the requested quantity can be simulated from the available liquidity evidence.

### Recommended workflow

Do not start with every execution feature. Begin with a market buy using zero costs and full volume participation. Verify point-in-time eligibility and exact-once accounting. Then introduce partial fills, costs, limit/stop semantics, cancellation, and risk controls one at a time.

### Common misunderstanding

A retained draft is not active. **Confirmation is a separate explicit action.** Even after confirmation, the order remains simulated-only and local.

## Data Sources

### What it is

Data Sources explains where governed evidence comes from and what OSCA is currently allowed to use.

### Use Data Sources for

- importing local CSV/Parquet history;
- using bundled or synthetic evidence;
- inspecting provider admission/policy state;
- explicitly acquiring supported no-cost provider data where admitted;
- diagnosing why an asset has no available Workbench data;
- inspecting credential metadata without exposing credential values.

### Recommended workflow

Prefer already-retained local evidence when it satisfies the research need. For crypto, admitted public provider acquisition may be available with explicit network opt-in. For unsupported/blocked equity sources, use governed local CSV/Parquet import rather than searching for an unofficial API shortcut.

### Common misunderstanding

A provider appearing in the catalog does not mean it is automatically usable. Licensing, plan, credential, quota, retention, and export policy can keep a provider blocked.

## Recommended workflows

### Workflow A — "I just want to inspect an asset"

**Workspace → Markets → Workbench**

If Workbench has no usable data, insert **Data Sources** before Workbench.

You do not need Projects, Strategy Lab, Portfolio Lab, or Paper Lab for a simple chart/table investigation.

### Workflow B — "I want to test a trading rule historically"

**Workspace → Data Sources/Markets → Workbench → Strategy Lab → Projects**

Use Workbench to verify the evidence first. Backtest in Strategy Lab. Save the strategy/backtest into a Project when the result is worth retaining.

### Workflow C — "I want to model owning assets without testing a strategy"

**Workspace → Portfolio Lab**

Use Markets/Workbench first only if you need to inspect the asset or obtain valuation evidence. Paper Lab is unnecessary unless you want simulated forward order execution.

### Workflow D — "I want to move from backtest to forward simulation"

**Workspace → Workbench → Strategy Lab → Projects → Portfolio Lab → Paper Lab**

This is the most complete D9 workflow:

1. verify historical evidence;
2. backtest and challenge the strategy;
3. retain the useful research evidence;
4. create a virtual portfolio;
5. create a paper account and execution assumptions;
6. retain and explicitly confirm a simulated order;
7. process later governed evidence;
8. compare forward behavior with the historical backtest descriptively.

### Workflow E — "Something says unavailable or degraded"

Start from the area showing the problem, then usually inspect **Data Sources** and **Workspace**.

Do not work around a degraded state by manually inventing values. OSCA intentionally fails closed when required evidence is missing or ambiguous.

## Finance terminology: minimal survival guide

| Term | Meaning in OSCA |
|---|---|
| **Asset / instrument** | A uniquely identified equity, cryptocurrency, or other supported market instrument. |
| **Bar** | One time bucket containing market observations such as OHLCV. |
| **Position** | Current quantity held in a portfolio. |
| **Lot** | One retained acquisition batch inside a position. |
| **Exposure** | Amount of portfolio value affected by an asset/currency. |
| **Equity** | Portfolio value when required valuation/FX evidence is complete. |
| **P&L** | Profit and loss; realized after disposal or unrealized while still held. |
| **Drawdown** | Decline from a previous equity peak. |
| **Spread** | Difference around the market price that makes execution less favorable. |
| **Slippage** | Additional difference between reference price and simulated execution price. |
| **Liquidity** | Evidence of how much can reasonably be filled; modeled with bar volume in D9. |
| **Cost basis / book cost** | Accounting cost retained for acquired holdings. |
| **Revision / provenance** | Identity and lineage of the exact evidence used to calculate a result. |

## What OSCA deliberately does not do

The desktop may become feature-rich, but these boundaries remain important:

- no live broker/exchange order submission;
- no real-capital trading;
- no autonomous live execution;
- no silent provider/network fetch;
- no fabricated values when required evidence is missing;
- no AI authority over accounting or deterministic calculations;
- no investment recommendation implied by a backtest or paper result.

## Documentation rule for future desktop areas

Every new or materially changed top-level desktop area must update this guide before its milestone can close. The update must include:

- a plain-language purpose;
- prerequisites;
- what the user should use the area for;
- what the area is **not** for;
- important domain terms introduced by the area;
- at least one recommended workflow showing how the area connects to the rest of OSCA;
- failure/degraded-state guidance where relevant.

If a workflow cannot be explained clearly enough for this guide, treat that as product usability evidence and reconsider the UI or workflow rather than documenting accidental complexity.