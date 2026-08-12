import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D4 exposes Markets as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Markets.tsx", import.meta.url), "utf8");
  assert.match(root, /"markets"/);
  assert.match(root, /MarketsSurface/);
  assert.match(surface, /Asset browser/);
  assert.match(surface, /Asset details/);
  assert.match(surface, /Recent assets/);
  assert.match(surface, /Watchlists/);
  assert.match(surface, /No streaming quotes or execution/);
});

test("D4 frontend wires all canonical asset and watchlist lifecycle methods", async () => {
  const api = await readFile(new URL("../src/marketsApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Markets.tsx", import.meta.url), "utf8");

  for (const method of [
    "asset.search",
    "asset.get",
    "asset.recent.list",
    "asset.recent.record",
    "watchlist.list",
    "watchlist.create",
    "watchlist.rename",
    "watchlist.delete",
    "watchlist.asset.add",
    "watchlist.asset.remove",
    "watchlist.reorder"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }

  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.match(surface, /Inspect/);
  assert.match(surface, /Rename active watchlist/);
  assert.match(surface, /Move .* up/);
  assert.match(surface, /Move .* down/);
  assert.doesNotMatch(api, /plugin-fs|plugin-shell|fetch\(|WebSocket|orders\.submit/);
});

test("D4 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/markets.css", import.meta.url), "utf8");
  assert.match(css, /max-width:680px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
});
