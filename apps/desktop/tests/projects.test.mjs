import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D6 exposes Projects as a first-class desktop area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Projects.tsx", import.meta.url), "utf8");

  assert.match(root, /"projects"/);
  assert.match(root, /ProjectsSurface/);
  assert.match(root, /Open a validated profile from Workspace before creating research projects/);
  assert.match(surface, /D6 research projects/);
  assert.match(surface, /Evidence pins/);
  assert.match(surface, /User notes/);
  assert.match(surface, /Saved workspaces/);
  assert.match(surface, /Timeline/);
  assert.match(surface, /Export manifest/);
});

test("D6 frontend wires only typed desktop project methods", async () => {
  const api = await readFile(new URL("../src/projectApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/Projects.tsx", import.meta.url), "utf8");

  for (const method of [
    "project.create",
    "project.list",
    "project.get",
    "project.update",
    "project.archive",
    "project.restore",
    "project.clone",
    "project.pin.add",
    "project.note.add",
    "project.workspace.save",
    "project.export.prepare"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }

  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.match(surface, /prepareProjectExport/);
  assert.match(surface, /Thin manifest/);
  assert.match(surface, /user-authored/);
  assert.doesNotMatch(api, /@tauri-apps\/plugin-fs|@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(`${api}\n${surface}`, /fetch\s*\(|WebSocket|provider_url|orders?\.submit|broker|notebook/i);
});

test("D6 frontend discloses degraded and non-self-contained project evidence", async () => {
  const surface = await readFile(new URL("../src/Projects.tsx", import.meta.url), "utf8");
  const api = await readFile(new URL("../src/projectApi.ts", import.meta.url), "utf8");

  assert.match(surface, /degraded_status/);
  assert.match(surface, /Declarative context only/);
  assert.match(surface, /Self-contained package/);
  assert.match(api, /thin_manifest/);
  assert.match(api, /self_contained_package/);
});

test("D6 responsive and accessibility safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/projects.css", import.meta.url), "utf8");

  assert.match(css, /max-width: 680px/);
  assert.match(css, /max-width: 320px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /forced-colors/);
  assert.match(css, /focus-visible/);
});
