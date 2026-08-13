import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D5 exposes Workbench as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Workbench.tsx", import.meta.url), "utf8");
  assert.match(root, /"workbench"/);
  assert.match(root, /WorkbenchSurface/);
  assert.match(surface, /Charting workbench/);
  assert.match(surface, /Synchronized displayed values/);
  assert.match(surface, /Saved workbench views/);
  assert.match(surface, /full-resolution CSV evidence/i);
  assert.match(surface, /Research only/);
});

test("D5 frontend uses only typed desktop workbench methods for authoritative analysis", async () => {
  const seriesApi = await readFile(new URL("../src/workbenchApi.ts", import.meta.url), "utf8");
  const lifecycleApi = await readFile(new URL("../src/workbenchLifecycleApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Workbench.tsx", import.meta.url), "utf8");

  for (const method of [
    "workbench.analysis.get",
    "workbench.comparison.get",
    "workbench.export.prepare",
    "workbench.view.list",
    "workbench.view.create",
    "workbench.view.update",
    "workbench.view.rename",
    "workbench.view.delete"
  ]) {
    assert.match(lifecycleApi, new RegExp(method.replaceAll(".", "\\.")));
  }
  assert.match(seriesApi, /workbench\.series\.get/);
  assert.match(seriesApi, /invoke<string>\("desktop_request"/);
  assert.match(lifecycleApi, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(seriesApi + lifecycleApi + surface, /fetch\(|WebSocket|orders\.submit|provider_url|plugin-shell/);

  for (const forbiddenFormula of [
    /100\s*-\s*100\s*\//,
    /covariance/i,
    /standardDeviation/i,
    /bollinger.*\+/i,
    /macd.*ema/i
  ]) {
    assert.doesNotMatch(surface, forbiddenFormula);
  }
});

test("D5 chart and accessible table share the same returned row collection", async () => {
  const surface = await readFile(new URL("../src/Workbench.tsx", import.meta.url), "utf8");
  assert.match(surface, /<PriceChart rows=\{result\.series\.rows\}/);
  assert.match(surface, /<AccessibleSeriesTable rows=\{result\.series\.rows\}/);
  assert.match(surface, /Exact displayed values are in the synchronized table/);
  assert.match(surface, /Display is downsampled for bounded rendering/);
});

test("D5 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/workbench.css", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Workbench.tsx", import.meta.url), "utf8");
  assert.match(css, /max-width:\s*680px/);
  assert.match(css, /max-width:\s*320px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(surface, /role="img"/);
  assert.match(surface, /aria-label=\{summary\}/);
  assert.match(surface, /tabIndex=\{0\}/);
  assert.match(surface, /aria-pressed/);
});
