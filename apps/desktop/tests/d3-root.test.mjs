import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D3 root exposes Data Sources as a first-class desktop area", async () => {
  const source = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const main = await readFile(new URL("../src/main.tsx", import.meta.url), "utf8");

  assert.match(source, /aria-label="Desktop areas"/);
  assert.match(source, />Data Sources</);
  assert.match(source, /aria-current=/);
  assert.match(source, /bootstrapDesktop/);
  assert.match(source, /DataSourcesSurface profileRoot=/);
  assert.match(source, /No profile selected/);
  assert.match(main, /<D3Root \/>/);
});

test("D3 composition preserves the narrow desktop authority boundary", async () => {
  const source = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(source, /@tauri-apps\/plugin-fs/);
  assert.doesNotMatch(source, /@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(source, /localStorage|sessionStorage/);
  assert.doesNotMatch(source, /fetch\s*\(/);
});

test("D3 mode navigation retains narrow and accessibility safeguards", async () => {
  const css = await readFile(new URL("../src/d3Root.css", import.meta.url), "utf8");
  assert.match(css, /@media \(max-width: 520px\)/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(css, /focus-visible/);
});
