import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("desktop navigation explains every top-level area in plain language", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const guidance = await readFile(new URL("../src/DesktopGuidance.tsx", import.meta.url), "utf8");

  assert.match(root, /menuHint\(item\)/);
  assert.match(root, /d3-mode-description/);
  assert.match(root, /DesktopAreaGuidance view=\{view\}/);

  for (const phrase of [
    "Profiles and app health",
    "Find assets to research",
    "Inspect charts and data",
    "Organize research evidence",
    "Test strategies historically",
    "Model virtual holdings",
    "Simulate future orders",
    "Import and govern data"
  ]) {
    assert.match(guidance, new RegExp(phrase));
  }
});

test("complex research areas provide progressive workflow guidance", async () => {
  const guidance = await readFile(new URL("../src/DesktopGuidance.tsx", import.meta.url), "utf8");

  assert.match(guidance, /<summary>What do I do here\?<\/summary>/);
  assert.match(guidance, /Run sensitivity and walk-forward checks/);
  assert.match(guidance, /Retain valuation evidence/);
  assert.match(guidance, /Retain the paper run and execution assumptions first/);
  assert.match(guidance, /If Retain draft is disabled/);
  assert.match(guidance, /simulated only and has no live-order path/);
});

test("desktop contextual guidance remains keyboard and narrow-width friendly", async () => {
  const css = await readFile(new URL("../src/d3Root.css", import.meta.url), "utf8");

  assert.match(css, /overflow-x: auto/);
  assert.match(css, /desktop-area-help summary:focus-visible/);
  assert.match(css, /min-height: 2\.75rem/);
  assert.match(css, /@media \(max-width: 700px\)/);
  assert.match(css, /forced-colors/);
  assert.match(css, /prefers-reduced-motion/);
});
