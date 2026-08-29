import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("D9 exposes Paper Lab as a first-class simulated research area", async () => {
  const root = await readFile(new URL("../src/D3Root.tsx", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  assert.match(root, /"paper-lab"/);
  assert.match(root, /PaperForwardLabSurface/);
  assert.match(root, /Open and own a validated profile from Workspace before using simulated Paper Lab/);
  assert.match(surface, /SIMULATED ONLY/);
  assert.match(surface, /There is no broker, exchange destination, live order API, or real-capital path/);
  assert.match(surface, /Retained M8 paper account/);
  assert.match(surface, /Confirm SIMULATED-ONLY order/);
  assert.match(surface, /It is not active until explicitly confirmed/);
  assert.match(surface, /Governed completed-bar evidence/);
  assert.match(surface, /Forward vs\. backtest evidence/);
  assert.match(surface, /Descriptive only/);
});

test("D9 renderer calls only typed desktop paper and retained-account boundaries", async () => {
  const api = await readFile(new URL("../src/paperForwardApi.ts", import.meta.url), "utf8");
  const accountApi = await readFile(new URL("../src/paperAccountApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  for (const method of [
    "paper.run.bind",
    "paper.run.inspect",
    "paper.assumptions.retain",
    "paper.order.draft.retain",
    "paper.order.confirm",
    "paper.order.cancel",
    "paper.order.process_bar",
    "paper.mark.append",
    "paper.checkpoint.record",
    "paper.comparison.build"
  ]) {
    assert.match(api, new RegExp(method.replaceAll(".", "\\.")));
  }
  for (const method of [
    "paper.account.list",
    "paper.account.create",
    "paper.account.control.record"
  ]) {
    assert.match(accountApi, new RegExp(method.replaceAll(".", "\\.")));
  }

  const combined = `${api}\n${accountApi}\n${surface}`;
  assert.match(combined, /invoke<string>\("desktop_request"/);
  assert.doesNotMatch(combined, /@tauri-apps\/plugin-fs|@tauri-apps\/plugin-shell/);
  assert.doesNotMatch(combined, /fetch\s*\(|WebSocket|provider_url|broker\.submit|orders?\.submit/i);
  assert.match(api, /broker_connections_enabled: false/);
  assert.match(api, /autonomous_execution_enabled: false/);
  assert.match(api, /live_order_execution: false/);
  assert.match(api, /real_capital_execution_enabled: false/);
});

test("D9 uses retained M8 paper accounts instead of synthesizing account identities", async () => {
  const accountApi = await readFile(new URL("../src/paperAccountApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  assert.match(accountApi, /export async function listPaperAccounts/);
  assert.match(accountApi, /export async function createPaperAccount/);
  assert.match(accountApi, /export async function recordPaperControl/);
  assert.match(surface, /await createPaperAccount/);
  assert.match(surface, /await recordPaperControl/);
  assert.match(surface, /Select retained paper account/);
  assert.match(surface, /Engage simulated kill switch/);
  assert.doesNotMatch(surface, /setPaperAccountId\(crypto\.randomUUID\(\)\)/);
  assert.doesNotMatch(surface, /useState<string>\(\(\) => crypto\.randomUUID\(\)\).*paperAccountId/);
});

test("D9 keeps immutable draft retention separate from explicit confirmation", async () => {
  const api = await readFile(new URL("../src/paperForwardApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  assert.match(api, /export async function retainPaperDraft/);
  assert.match(api, /export async function confirmPaperDraft/);
  assert.match(surface, /await retainPaperDraft\(profileRoot, input\)/);
  assert.match(surface, /await confirmPaperDraft\(profileRoot, paperRunId, draftId, draftVersion\)/);
  assert.match(surface, /Retain draft v/);
  assert.match(surface, /Confirm SIMULATED-ONLY order/);
});

test("D9 new bar evidence inherits draft series identity", async () => {
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  assert.match(surface, /newBar\(instrumentId, datasetRevisionId, timeframe\)/);
  assert.match(surface, /instrumentId,/);
  assert.match(surface, /datasetRevisionId,/);
  assert.match(surface, /timeframe/);
  assert.match(surface, /New bars inherit the draft instrument/);
});

test("D9 renderer surfaces authoritative no-fill decisions instead of generic success", async () => {
  const api = await readFile(new URL("../src/paperForwardApi.ts", import.meta.url), "utf8");

  assert.match(api, /object\(record\.step, "step"\)/);
  assert.match(api, /object\(step\.decision, "step\.decision"\)/);
  assert.match(api, /decision\.can_fill/);
  assert.match(api, /code: "paper_no_fill"/);
  assert.match(api, /No simulated fill:/);
  assert.match(api, /step\.decision\.reason/);
});

test("D9 Paper Lab accessibility and responsive safeguards are explicit", async () => {
  const css = await readFile(new URL("../src/paperForwardLab.css", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/PaperForwardLab.tsx", import.meta.url), "utf8");

  assert.match(css, /min-height: 44px/);
  assert.match(css, /focus-visible/);
  assert.match(css, /forced-colors/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /overflow-x: auto/);
  assert.match(css, /max-width: 700px/);
  assert.match(surface, /role="note"/);
  assert.match(surface, /role=\{feedback\.kind === "error" \? "alert" : "status"\}/);
  assert.match(surface, /aria-label="Simulation safety boundary"/);
  assert.match(surface, /aria-label="Descriptive comparison evidence"/);
});