import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("data sources surface exposes offline, provider, acquisition, and evidence regions", async () => {
  const surface = await readFile(new URL("../src/DataSources.tsx", import.meta.url), "utf8");
  assert.match(surface, /Data Sources/);
  assert.match(surface, /Free offline paths/);
  assert.match(surface, /Provider policy/);
  assert.match(surface, /Kraken public OHLC/);
  assert.match(surface, /Retained acquisition evidence/);
  assert.match(surface, /Network opt-in/);
  assert.match(surface, /Live execution off/);
  assert.match(surface, /synchronous, request-scoped operation/);
  assert.match(surface, /id="kraken-network-consent"/);
  assert.match(surface, /Allow this single request to contact Kraken over HTTPS/);
});

test("D3 frontend uses the canonical acquisition contracts", async () => {
  const api = await readFile(new URL("../src/dataSourcesApi.ts", import.meta.url), "utf8");
  assert.ok(api.includes('request("acquisition.run"'));
  assert.ok(api.includes("record.evidence"));
  assert.ok(api.includes("record.acquisitions"));
  assert.ok(!api.includes("acquisition.submit"));
});

test("D3 frontend retains the narrow desktop request bridge and no generic native authority", async () => {
  const api = await readFile(new URL("../src/dataSourcesApi.ts", import.meta.url), "utf8");
  const surface = await readFile(new URL("../src/DataSources.tsx", import.meta.url), "utf8");
  const combined = `${api}\n${surface}`;
  assert.match(api, /invoke<string>\("desktop_request"/);
  assert.match(api, /provider\.catalog/);
  assert.match(api, /credential\.store/);
  assert.match(api, /local\.import/);
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
  assert.match(css, /\.consent-row input/);
  assert.match(surface, /role=\{notice\.tone === "error" \? "alert" : "status"\}/);
  assert.match(surface, /type="password"/);
  assert.match(surface, /Explicit network consent is required/);
});
