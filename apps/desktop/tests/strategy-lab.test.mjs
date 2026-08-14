import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D7 exposes Strategy Lab as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/StrategyLab.tsx", import.meta.url), "utf8");

  assert.match(root, /"strategy-lab"/);
  assert.match(root, /StrategyLabSurface/);
  assert.match(root, /Open a validated profile from Workspace before using Strategy Lab/);
  assert.match(surface, /D7 strategy research/);
  assert.match(surface, /Guided SMA strategy/);
  assert.match(surface, /Backtest evidence/);
  assert.match(surface, /Manifest:/);
  assert.match(surface, /BacktestCurve/);
  assert.match(surface, /SelectedObservation/);
  assert.match(surface, /Run sensitivity/);
  assert.match(surface, /Run walk-forward/);
});

test("D7 frontend wires only typed desktop strategy and backtest methods", async () => {
  const api = await readFile(new URL("../src/strategyApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/StrategyLab.tsx", import.meta.url), "utf8");

  for (const method of [
    "strategy.create",
    "strategy.list",
    "strategy.version.create",
    "strategy.validate",
    "backtest.run",
    "backtest.cancel",
    "backtest.export.prepare",
    "backtest.sensitivity.run",
    "backtest.walkforward.run"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }

  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.match(surface, /No execution/);
  assert.match(surface, /Python-authoritative backtest/);
  assert.doesNotMatch(api, /@tauri-apps\/plugin-fs|@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(`${api}\n${surface}`, /fetch\s*\(|WebSocket|provider_url|orders?\.submit|broker|notebook/i);
});

test("D7 result inspection has synchronized keyboard and pointer chart parity", async () => {
  const api = await readFile(new URL("../src/strategyApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/StrategyLab.tsx", import.meta.url), "utf8");

  assert.match(api, /equity_curve: BacktestPoint\[\]/);
  assert.match(api, /trades: BacktestTrade\[\]/);
  assert.match(surface, /onKeyDown=\{handleKeyDown\}/);
  assert.match(surface, /ArrowLeft/);
  assert.match(surface, /ArrowRight/);
  assert.match(surface, /Home/);
  assert.match(surface, /End/);
  assert.match(surface, /onClick=\{\(\) => setSelectedIndex\(index\)\}/);
  assert.match(surface, /Selected observation/);
  assert.match(surface, /Timestamp/);
  assert.match(surface, /Drawdown/);
});

test("D7 export exposes full-resolution result tables without embedding provider datasets", async () => {
  const api = await readFile(new URL("../src/strategyApi.ts", import.meta.url), "utf8");
  const testSource = await readFile(new URL("../../../tests/test_d7_desktop_strategies.py", import.meta.url), "utf8");

  assert.match(api, /data_paths: string\[\]/);
  assert.match(testSource, /backtest-\{result_id\}\.equity\.csv|timestamp,close,equity,drawdown,signal/);
  assert.match(testSource, /timestamp,side,fill_price,quantity,fees,research_assumption/);
  assert.match(testSource, /provider_datasets_embedded"\] is False/);
});

test("D7 sensitivity and walk-forward controls expose bounded evaluation evidence", async () => {
  const api = await readFile(new URL("../src/strategyApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/StrategyLab.tsx", import.meta.url), "utf8");

  assert.match(api, /BacktestEvaluation/);
  assert.match(api, /runSensitivity/);
  assert.match(api, /runWalkforward/);
  assert.match(api, /cancelEvaluation/);
  assert.match(surface, /EvaluationPanel/);
  assert.match(surface, /Budget and cancellation behavior/);
  assert.match(surface, /Walk-forward train and test partitions/);
  assert.match(surface, /Evaluation result rows/);
});

test("D7 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/strategyLab.css", import.meta.url), "utf8");

  assert.match(css, /max-width: 680px/);
  assert.match(css, /max-width: 320px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(css, /focus-visible/);
  assert.match(css, /strategy-chart-svg/);
  assert.match(css, /strategy-point-selected/);
});
