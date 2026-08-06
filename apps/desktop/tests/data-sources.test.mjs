import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test, { after } from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

const server = await createServer({ appType: "custom", server: { middlewareMode: true } });
after(async () => server.close());

const { DataSourcesSurface } = await server.ssrLoadModule("/src/DataSources.tsx");

test("data sources surface exposes offline, provider, acquisition, and evidence regions", () => {
  const html = renderToStaticMarkup(React.createElement(DataSourcesSurface, { profileRoot: "/tmp/osca-profile" }));
  assert.match(html, /Data Sources/);
  assert.match(html, /Free offline paths/);
  assert.match(html, /Provider policy/);
  assert.match(html, /Kraken public OHLC/);
  assert.match(html, /Retained acquisition evidence/);
  assert.match(html, /Network opt-in/);
  assert.match(html, /Live execution off/);
  assert.match(html, /synchronous, request-scoped operation/);
});

test("D3 frontend retains the narrow desktop request bridge and no generic native authority", async () => {
  const api = await readFile(new URL("../src/dataSourcesApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/DataSources.tsx", import.meta.url), "utf8");
  const combined = `${api}\n${surface}`;
  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.match(api, /provider\.catalog/);
  assert.match(api, /credential\.store/);
  assert.match(api, /local\.import/);
  assert.match(api, /acquisition\.submit/);
  assert.match(api, /acquisition\.list/);
  assert.doesNotMatch(combined, /plugin-fs|plugin-shell|node:fs|sqlite|parquet|orders\.submit/);
  assert.doesNotMatch(surface, /secret_value_returned\s*:\s*true/);
});

test("responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/dataSources.css", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/DataSources.tsx", import.meta.url), "utf8");
  assert.match(css, /max-width:680px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(surface, /role=\{notice\.tone === "error" \? "alert" : "status"\}/);
  assert.match(surface, /type="password"/);
  assert.match(surface, /Explicit network consent is required/);
});
