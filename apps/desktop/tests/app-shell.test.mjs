import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test, { after } from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

const server = await createServer({
  appType: "custom",
  server: { middlewareMode: true }
});

after(async () => {
  await server.close();
});

const { App } = await server.ssrLoadModule("/src/App.tsx");

test("initial shell preserves navigation, loading, and permanent safety boundaries", () => {
  const html = renderToStaticMarkup(React.createElement(App));

  assert.match(html, /Skip to main content/);
  assert.match(html, /id="main-content"/);
  assert.match(html, /Preparing OSCA/);
  assert.match(html, /Loading your local workspace/);
  assert.match(html, />Home</);
  assert.match(html, />System</);
  assert.match(html, />Research</);
  assert.match(html, />Evidence</);
  assert.match(html, /Later/);
  assert.match(html, /Network off/);
  assert.match(html, /Live execution off/);
  assert.match(html, /OSCA is research and simulation software, not financial advice/);
  assert.match(html, /Permanent product boundaries/);
});

test("frontend source uses only the narrow Tauri desktop request capability", async () => {
  const apiSource = await readFile(new URL("../src/api.ts", import.meta.url), "utf8");
  const appSource = await readFile(new URL("../src/App.tsx", import.meta.url), "utf8");
  const combined = `${apiSource}\n${appSource}`;

  assert.match(apiSource, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(combined, /@tauri-apps\/plugin-fs/);
  assert.doesNotMatch(combined, /@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(combined, /node:fs/);
  assert.doesNotMatch(combined, /sqlite/i);
  assert.doesNotMatch(combined, /parquet/i);
  assert.doesNotMatch(combined, /orders\.submit/);
});
