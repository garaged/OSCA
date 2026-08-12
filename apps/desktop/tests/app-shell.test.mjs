import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test, { after } from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

const server = await createServer({
  appType: "custom",
  optimizeDeps: { noDiscovery: true },
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

test("broker profile ownership failures are surfaced as profile locks", async () => {
  const apiSource = await readFile(new URL("../src/api.ts", import.meta.url), "utf8");

  assert.match(apiSource, /function classifyInvokeFailure/);
  assert.match(apiSource, /profile is already open in another OSCA window or process/);
  assert.match(apiSource, /profile mutation requires this OSCA window to open and own the profile first/);
  assert.match(apiSource, /code: "profile_locked"/);
  assert.match(apiSource, /throw new DesktopClientError\(classifyInvokeFailure\(error\)\)/);
});

test("native window permits the specified 320 CSS-pixel responsive foundation", async () => {
  const configSource = await readFile(
    new URL("../src-tauri/tauri.conf.json", import.meta.url),
    "utf8"
  );
  const config = JSON.parse(configSource);
  const primaryWindow = config.app.windows[0];

  assert.equal(primaryWindow.minWidth, 320);
  assert.ok(primaryWindow.minHeight <= 480);
});

test("native desktop CSP is enabled and local-only", async () => {
  const configSource = await readFile(
    new URL("../src-tauri/tauri.conf.json", import.meta.url),
    "utf8"
  );
  const config = JSON.parse(configSource);
  const csp = config.app.security.csp;
  const devCsp = config.app.security.devCsp;

  assert.equal(csp["default-src"], "'self'");
  assert.equal(csp["connect-src"], "ipc: http://ipc.localhost");
  assert.equal(csp["object-src"], "'none'");
  assert.equal(csp["base-uri"], "'none'");
  assert.equal(csp["frame-src"], "'none'");
  assert.doesNotMatch(JSON.stringify(csp), /https:\/\//);
  assert.doesNotMatch(JSON.stringify(csp), /'unsafe-eval'/);

  assert.match(devCsp["connect-src"], /ipc:/);
  assert.match(devCsp["connect-src"], /http:\/\/localhost:1420/);
  assert.match(devCsp["connect-src"], /ws:\/\/localhost:1420/);
  assert.doesNotMatch(JSON.stringify(devCsp), /https:\/\//);
  assert.doesNotMatch(JSON.stringify(devCsp), /0\.0\.0\.0/);
});
