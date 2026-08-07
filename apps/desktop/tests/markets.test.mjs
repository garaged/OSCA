import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D4 exposes Markets as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Markets.tsx", import.meta.url), "utf8");
  assert.match(root, /"markets"/);
  assert.match(root, /MarketsSurface/);
  assert.match(surface, /Asset browser/);
  assert.match(surface, /Watchlists/);
  assert.match(surface, /No streaming quotes or execution/);
});

test("D4 frontend uses canonical typed desktop methods only", async () => {
  const api = await readFile(new URL("../src/marketsApi.ts", import.meta.url), "utf8");
  assert.match(api, /asset\.search/);
  assert.match(api, /asset\.get/);
  assert.match(api, /watchlist\.list/);
  assert.match(api, /watchlist\.asset\.add/);
  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(api, /plugin-fs|plugin-shell|fetch\(|WebSocket|orders\.submit/);
});

test("D4 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/markets.css", import.meta.url), "utf8");
  assert.match(css, /max-width:680px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
});
