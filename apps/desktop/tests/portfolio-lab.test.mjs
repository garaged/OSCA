import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D8 exposes Portfolio Lab as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PortfolioLab.tsx", import.meta.url), "utf8");
  const analytics = await readFile(new URL("../src/PortfolioAnalytics.tsx", import.meta.url), "utf8");

  assert.match(root, /"portfolio-lab"/);
  assert.match(root, /PortfolioLabSurface/);
  assert.match(root, /PortfolioAnalyticsSurface/);
  assert.match(root, /Open a validated profile from Workspace before using Portfolio Lab/);
  assert.match(surface, /Append-only journal/);
  assert.match(surface, /No real capital/);
  assert.match(surface, /Valuation evidence incomplete/);
  assert.match(surface, /Immutable journal evidence/);
  assert.match(analytics, /Performance, attribution and scenarios/);
  assert.match(analytics, /Capture snapshot/);
  assert.match(analytics, /Descriptive benchmark/);
  assert.match(analytics, /Portfolio mutated/);
});

test("D8 frontend wires only typed portfolio research methods", async () => {
  const api = await readFile(new URL("../src/portfolioApi.ts", import.meta.url), "utf8");
  const analyticsApi = await readFile(
    new URL("../src/portfolioAnalyticsApi.ts", import.meta.url),
    "utf8"
  );
  const surface = await readFile(new URL("../src/PortfolioLab.tsx", import.meta.url), "utf8");
  const analytics = await readFile(new URL("../src/PortfolioAnalytics.tsx", import.meta.url), "utf8");

  for (const method of [
    "portfolio.list",
    "portfolio.get",
    "portfolio.create",
    "portfolio.acquisition.record",
    "portfolio.valuation.record"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }
  for (const method of [
    "portfolio.analytics.snapshot.capture",
    "portfolio.analytics.report",
    "portfolio.analytics.scenario",
    "portfolio.analytics.benchmark"
  ]) {
    assert.match(analyticsApi, new RegExp(method.replaceAll(".", "\\.")));
  }

  const combined = `${api}\n${analyticsApi}\n${surface}\n${analytics}`;
  assert.match(combined, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(combined, /@tauri-apps\/plugin-fs|@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(combined, /fetch\s*\(|WebSocket|provider_url|orders?\.submit|broker\.submit/i);
  assert.match(combined, /recommendations_enabled/);
  assert.match(combined, /real_capital_execution_enabled/);
});

test("D8 analytical controls keep exact decimal inputs and non-mutating scenarios", async () => {
  const api = await readFile(new URL("../src/portfolioAnalyticsApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PortfolioAnalytics.tsx", import.meta.url), "utf8");

  assert.match(api, /asset_shocks: assetShocks/);
  assert.match(api, /fx_shocks: fxShocks/);
  assert.match(api, /mutated_portfolio: false/);
  assert.match(api, /descriptive_only: true/);
  assert.match(surface, /Asset shock \(decimal\)/);
  assert.match(surface, /Scenario calculated from a projection copy/);
  assert.match(surface, /Benchmark comparison is descriptive research evidence only/);
});

test("D8 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/portfolioLab.css", import.meta.url), "utf8");
  const analyticsCss = await readFile(
    new URL("../src/portfolioAnalytics.css", import.meta.url),
    "utf8"
  );

  assert.match(css, /max-width: 760px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(css, /focus-visible/);
  assert.match(css, /min-height: 2\.5rem/);
  assert.match(css, /overflow-x: auto/);
  assert.match(analyticsCss, /max-width: 28rem/);
});
