import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  AcquisitionEvidence,
  DataSourcesClientError,
  deleteProviderCredential,
  fetchProviderCatalog,
  importLocalOhlcv,
  listAcquisitionEvidence,
  probeProviderCredential,
  ProviderCatalog,
  ProviderRow,
  storeProviderCredential,
  submitKrakenAcquisition
} from "./dataSourcesApi";
import "./dataSources.css";

type LoadState =
  | { kind: "loading" }
  | { kind: "ready"; value: ProviderCatalog }
  | { kind: "error"; error: DataSourcesClientError };

type Notice = { tone: "info" | "success" | "error"; message: string } | null;

export function DataSourcesSurface({ profileRoot }: { profileRoot?: string }) {
  const [catalog, setCatalog] = useState<LoadState>({ kind: "loading" });
  const [notice, setNotice] = useState<Notice>(null);
  const [secretValues, setSecretValues] = useState<Record<string, string>>({});
  const [inputPath, setInputPath] = useState("");
  const [symbol, setSymbol] = useState("XBTUSD");
  const [timeframe, setTimeframe] = useState("1d");
  const [networkConsent, setNetworkConsent] = useState(false);
  const [evidence, setEvidence] = useState<AcquisitionEvidence[]>([]);
  const noticeRef = useRef<HTMLDivElement>(null);

  async function reload() {
    setCatalog({ kind: "loading" });
    try {
      const value = await fetchProviderCatalog();
      setCatalog({ kind: "ready", value });
    } catch (error) {
      setCatalog({ kind: "error", error: asError(error) });
    }
  }

  async function reloadEvidence() {
    if (!profileRoot) {
      setEvidence([]);
      return;
    }
    try {
      setEvidence(await listAcquisitionEvidence(profileRoot));
    } catch (error) {
      setNotice({ tone: "error", message: asError(error).message });
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  useEffect(() => {
    void reloadEvidence();
  }, [profileRoot]);

  useEffect(() => {
    noticeRef.current?.focus();
  }, [notice]);

  const kraken = useMemo(
    () => catalog.kind === "ready" ? catalog.value.providers.find((row) => row.provider_id === "kraken") : undefined,
    [catalog]
  );

  async function runCredential(provider: ProviderRow, operation: "store" | "probe" | "delete") {
    try {
      const result = operation === "store"
        ? await storeProviderCredential(provider.provider_id, secretValues[provider.provider_id] ?? "")
        : operation === "probe"
          ? await probeProviderCredential(provider.provider_id)
          : await deleteProviderCredential(provider.provider_id);
      setSecretValues((current) => ({ ...current, [provider.provider_id]: "" }));
      setNotice({
        tone: "success",
        message: `${provider.provider_id}: credential ${result.operation}; vault state ${result.state}. Provider admission remains ${result.admission_status}.`
      });
      await reload();
    } catch (error) {
      setNotice({ tone: "error", message: asError(error).message });
    }
  }

  async function handleImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profileRoot) {
      setNotice({ tone: "error", message: "Open a compatible local profile before importing data." });
      return;
    }
    try {
      const result = await importLocalOhlcv({
        profile_root: profileRoot,
        input_path: inputPath,
        symbol,
        timeframe,
        source_uri: "local-file://user-supplied",
        calendar_assumption: "source-provided"
      });
      setNotice({ tone: "success", message: `Local import ${result.status}. Networking and credentials remained disabled.` });
    } catch (error) {
      setNotice({ tone: "error", message: asError(error).message });
    }
  }

  async function handleAcquire(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profileRoot) {
      setNotice({ tone: "error", message: "Open a compatible local profile before acquiring data." });
      return;
    }
    if (!networkConsent) {
      setNotice({ tone: "error", message: "Explicit network consent is required for this acquisition request." });
      return;
    }
    try {
      const result = await submitKrakenAcquisition({
        profile_root: profileRoot,
        provider_id: "kraken",
        asset_class: "crypto",
        symbol,
        timeframe,
        network_access_enabled: true
      });
      setNotice({ tone: result.status === "succeeded" || result.status === "fresh" ? "success" : "info", message: `${result.provider_id} acquisition ${result.status}: ${result.rationale}` });
      setNetworkConsent(false);
      await reloadEvidence();
    } catch (error) {
      setNotice({ tone: "error", message: asError(error).message });
    }
  }

  return (
    <section className="data-sources" aria-labelledby="data-sources-heading">
      <header className="data-sources-hero">
        <div>
          <p className="eyebrow">D3 data onboarding</p>
          <h1 id="data-sources-heading" tabIndex={-1}>Data Sources</h1>
          <p>Inspect provider policy, manage named credentials through the operating-system vault, import governed CSV evidence, and explicitly request approved public data.</p>
        </div>
        <div className="data-sources-boundaries" aria-label="Permanent safety boundaries">
          <span>Research only</span><span>Local-first</span><span>Network opt-in</span><span>Live execution off</span>
        </div>
      </header>

      {notice ? <div className={`data-notice data-notice-${notice.tone}`} ref={noticeRef} role={notice.tone === "error" ? "alert" : "status"} tabIndex={-1}>{notice.message}</div> : null}

      <section className="data-panel" aria-labelledby="offline-heading">
        <h2 id="offline-heading">Free offline paths</h2>
        <p>Bundled synthetic data and governed local CSV import never require a provider account, credential, or network request.</p>
        <form className="data-form" onSubmit={(event) => void handleImport(event)}>
          <label htmlFor="local-input-path">Absolute CSV path</label>
          <input id="local-input-path" value={inputPath} onChange={(event) => setInputPath(event.target.value)} required />
          <div className="data-form-row">
            <label>Symbol<input value={symbol} onChange={(event) => setSymbol(event.target.value)} required /></label>
            <label>Timeframe<select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>{["1m", "5m", "15m", "30m", "1h", "4h", "1d"].map((value) => <option key={value}>{value}</option>)}</select></label>
          </div>
          <button type="submit" disabled={!profileRoot}>Import local OHLCV</button>
        </form>
      </section>

      <section className="data-panel" aria-labelledby="providers-heading">
        <div className="data-section-heading"><h2 id="providers-heading">Provider policy</h2><button type="button" onClick={() => void reload()}>Refresh catalog</button></div>
        {catalog.kind === "loading" ? <p role="status">Loading provider policy…</p> : null}
        {catalog.kind === "error" ? <div role="alert"><p>{catalog.error.message}</p><button type="button" onClick={() => void reload()}>Retry</button></div> : null}
        {catalog.kind === "ready" ? <div className="provider-grid">{catalog.value.providers.map((provider) => <ProviderCard key={provider.provider_id} provider={provider} secretValue={secretValues[provider.provider_id] ?? ""} onSecretChange={(value) => setSecretValues((current) => ({ ...current, [provider.provider_id]: value }))} onCredential={runCredential} />)}</div> : null}
      </section>

      <section className="data-panel" aria-labelledby="acquisition-heading">
        <h2 id="acquisition-heading">Kraken public OHLC</h2>
        <p>This is a synchronous, request-scoped operation. The UI does not claim live background progress or active cancellation.</p>
        <form className="data-form" onSubmit={(event) => void handleAcquire(event)}>
          <div className="data-form-row"><label>Crypto pair<input value={symbol} onChange={(event) => setSymbol(event.target.value)} required /></label><label>Timeframe<select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>{["1m", "5m", "15m", "30m", "1h", "4h", "1d"].map((value) => <option key={value}>{value}</option>)}</select></label></div>
          <label className="consent-row"><input type="checkbox" checked={networkConsent} onChange={(event) => setNetworkConsent(event.target.checked)} />Allow this single request to contact Kraken over HTTPS.</label>
          <button type="submit" disabled={!profileRoot || !kraken?.acquisition_available}>Acquire public OHLC</button>
        </form>
      </section>

      <section className="data-panel" aria-labelledby="evidence-heading">
        <div className="data-section-heading"><h2 id="evidence-heading">Retained acquisition evidence</h2><button type="button" disabled={!profileRoot} onClick={() => void reloadEvidence()}>Refresh evidence</button></div>
        {evidence.length === 0 ? <p>No retained acquisition evidence is available for the open profile.</p> : <ul className="evidence-list">{evidence.map((item) => <li key={item.acquisition_id}><strong>{item.provider_id} {item.symbol} {item.timeframe}</strong><span>Status: {item.status}</span><span>Revision: {item.dataset_revision_id ?? "none"}</span><span>Rows: {item.canonical_row_count ?? "not available"}</span><p>{item.rationale}</p></li>)}</ul>}
      </section>
    </section>
  );
}

function ProviderCard({ provider, secretValue, onSecretChange, onCredential }: { provider: ProviderRow; secretValue: string; onSecretChange: (value: string) => void; onCredential: (provider: ProviderRow, operation: "store" | "probe" | "delete") => Promise<void> }) {
  const namedSecret = provider.credential_mode === "named-secret-reference";
  return <article className="provider-card"><div className="provider-title"><h3>{provider.provider_id}</h3><span data-status={provider.admission_status}>{provider.admission_status}</span></div><p>{provider.rationale}</p><dl><div><dt>Credential</dt><dd>{provider.credential_state}</dd></div><div><dt>Network</dt><dd>{provider.network_required ? "Explicit request required" : "Not required"}</dd></div><div><dt>Reviewed</dt><dd>{provider.evidence_reviewed_at}</dd></div></dl>{provider.findings.length ? <ul>{provider.findings.map((finding) => <li key={finding}>{finding}</li>)}</ul> : null}{namedSecret ? <div className="credential-controls"><label htmlFor={`secret-${provider.provider_id}`}>Replace credential<input id={`secret-${provider.provider_id}`} type="password" autoComplete="off" value={secretValue} onChange={(event) => onSecretChange(event.target.value)} /></label><div><button type="button" onClick={() => void onCredential(provider, "store")}>Store</button><button type="button" onClick={() => void onCredential(provider, "probe")}>Probe</button><button className="destructive" type="button" onClick={() => void onCredential(provider, "delete")}>Delete</button></div><p>The value is sent only to Python for OS-vault storage and is never returned.</p></div> : null}</article>;
}

function asError(error: unknown): DataSourcesClientError {
  return error instanceof DataSourcesClientError ? error : new DataSourcesClientError("unexpected_error", error instanceof Error ? error.message : "Unexpected data-source failure.");
}
