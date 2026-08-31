import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D10 exposes ML Lab as a first-class governed research area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/MLLab.tsx", import.meta.url), "utf8");

  assert.match(root, /"ml-lab"/);
  assert.match(root, /MLLabSurface/);
  assert.match(root, /Open a validated profile from Workspace before using ML Lab/);
  assert.match(surface, /Governed feature catalog/);
  assert.match(surface, /Dataset and experiment builder/);
  assert.match(surface, /Experiment registry/);
  assert.match(surface, /Test evidence versus mandatory baseline/);
});

test("D10 renderer uses only typed ML desktop methods", async () => {
  const api = await readFile(new URL("../src/mlLabApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/MLLab.tsx", import.meta.url), "utf8");

  for (const method of [
    "ml.catalog.list",
    "ml.experiment.create",
    "ml.experiment.run",
    "ml.experiment.list",
    "ml.experiment.cancel"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }
  const combined = `${api}\n${surface}`;
  assert.match(combined, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(combined, /@tauri-apps\/plugin-fs|@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(combined, /fetch\s*\(|WebSocket|provider_url|broker\.submit|orders?\.submit/i);
  assert.match(surface, /No automatic promotion/);
  assert.match(surface, /No recommendation or execution/);
});

test("D10 visibly retains temporal and data policy evidence", async () => {
  const surface = await readFile(new URL("../src/MLLab.tsx", import.meta.url), "utf8");

  assert.match(surface, /Chronological 60\/20\/20 split/);
  assert.match(surface, /horizon purge/);
  assert.match(surface, /Single-asset survivorship/);
  assert.match(surface, /governed corporate-action semantics/);
  assert.match(surface, /missing data fails closed/);
  assert.match(surface, /Purge \/ embargo/);
});

test("D10 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/mlLab.css", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/MLLab.tsx", import.meta.url), "utf8");

  assert.match(css, /min-height: 44px/);
  assert.match(css, /focus-visible/);
  assert.match(css, /forced-colors/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /max-width: 700px/);
  assert.match(css, /max-width: 320px/);
  assert.match(surface, /aria-label="ML safety boundary"/);
  assert.match(surface, /role="note"/);
  assert.match(surface, /role="alert"/);
});
