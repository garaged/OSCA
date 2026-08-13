import { FormEvent, KeyboardEvent, useEffect, useMemo, useState } from "react";
import { importBundledSample, SampleImportResult } from "./api";
import { Asset, searchAssets } from "./marketsApi";
import {
  getWorkbenchSeries,
  WorkbenchClientError,
  WorkbenchDerivedRequest,
  WorkbenchRange,
  WorkbenchRow,
  WorkbenchSeries
} from "./workbenchApi";
import {
  ComparisonResult,
  createWorkbenchView,
  deleteWorkbenchView,
  getComparison,
  getQuantitativeAnalysis,
  listWorkbenchViews,
  prepareWorkbenchExport,
  QuantitativeAnalysis,
  renameWorkbenchView,
  SavedWorkbenchView,
  updateWorkbenchView,
  WorkbenchExport
} from "./workbenchLifecycleApi";
import "./workbench.css";

type LoadState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; value: WorkbenchSeries }
  | { kind: "error"; error: WorkbenchClientError };

type AssetState =
  | { kind: "loading" }
  | { kind: "ready"; assets: Asset[] }
  | { kind: "error"; message: string };

type AsyncResult<T> =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; value: T }
  | { kind: "error"; message: string };

const WIDTH = 900;
const HEIGHT = 360;
const VOLUME_HEIGHT = 120;
const PADDING = 28;
const PRICE_AXIS_PADDING = 72;
const DISPLAY_ROWS = 240;

export function WorkbenchSurface({ profileRoot }: { profileRoot?: string }) {
  const [assets, setAssets] = useState<AssetState>({ kind: "loading" });
  const [assetId, setAssetId] = useState("equity:XNAS:AAPL");
  const [comparisonAssetId, setComparisonAssetId] = useState("equity:XNAS:MSFT");
  const [timeframe, setTimeframe] = useState("1d");
  const [rangeStart, setRangeStart] = useState("");
  const [rangeEnd, setRangeEnd] = useState("");
  const [indicator, setIndicator] = useState<WorkbenchDerivedRequest["kind"] | "none">("sma");
  const [windowSize, setWindowSize] = useState(3);
  const [state, setState] = useState<LoadState>({ kind: "idle" });
  const [analysis, setAnalysis] = useState<AsyncResult<QuantitativeAnalysis>>({ kind: "idle" });
  const [comparison, setComparison] = useState<AsyncResult<ComparisonResult>>({ kind: "idle" });
  const [exportState, setExportState] = useState<AsyncResult<WorkbenchExport>>({ kind: "idle" });
  const [sampleImport, setSampleImport] = useState<AsyncResult<SampleImportResult>>({ kind: "idle" });
  const [views, setViews] = useState<AsyncResult<SavedWorkbenchView[]>>({ kind: "idle" });
  const [viewName, setViewName] = useState("");
  const [activeViewId, setActiveViewId] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    setAssets({ kind: "loading" });
    void searchAssets("", profileRoot)
      .then((result) => {
        if (cancelled) return;
        setAssets({ kind: "ready", assets: result.assets });
        if (!result.assets.some((asset) => asset.asset_id === assetId) && result.assets[0]) {
          setAssetId(result.assets[0].asset_id);
        }
        const alternative = result.assets.find((asset) => asset.asset_id !== assetId);
        if (alternative && !result.assets.some((asset) => asset.asset_id === comparisonAssetId)) {
          setComparisonAssetId(alternative.asset_id);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setAssets({
            kind: "error",
            message: error instanceof Error ? error.message : "Asset catalog unavailable."
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [profileRoot]);

  useEffect(() => {
    if (!profileRoot) return;
    void refreshViews(profileRoot);
  }, [profileRoot]);

  function derivedRequest(
    selectedIndicator: WorkbenchDerivedRequest["kind"] | "none" = indicator,
    selectedWindow = windowSize
  ): WorkbenchDerivedRequest[] {
    if (selectedIndicator === "none") return [];
    if (selectedIndicator === "simple_return" || selectedIndicator === "log_return") {
      return [{ kind: selectedIndicator }];
    }
    return [{ kind: selectedIndicator, window: selectedWindow }];
  }

  function requestedRange(): WorkbenchRange {
    return {
      ...(rangeStart.trim() ? { start: rangeStart.trim() } : {}),
      ...(rangeEnd.trim() ? { end: rangeEnd.trim() } : {})
    };
  }

  function currentConfig(): Record<string, unknown> {
    return {
      primary_asset_id: assetId,
      comparison_asset_id: comparisonAssetId,
      timeframe,
      range: requestedRange(),
      max_rows: DISPLAY_ROWS,
      derived: derivedRequest(),
      layout: { volume_visible: true, table_visible: true }
    };
  }

  async function refreshViews(root: string) {
    setViews({ kind: "loading" });
    try {
      setViews({ kind: "ready", value: await listWorkbenchViews(root) });
    } catch (error) {
      setViews({ kind: "error", message: errorMessage(error) });
    }
  }

  async function load(event?: FormEvent) {
    event?.preventDefault();
    await loadSeries(assetId, timeframe, derivedRequest(), requestedRange());
  }

  async function loadSeries(
    selectedAssetId: string,
    selectedTimeframe: string,
    selectedDerived: WorkbenchDerivedRequest[],
    selectedRange: WorkbenchRange
  ) {
    if (!profileRoot) return;
    setState({ kind: "loading" });
    setAnalysis({ kind: "idle" });
    setComparison({ kind: "idle" });
    setExportState({ kind: "idle" });
    try {
      const value = await getWorkbenchSeries(
        profileRoot,
        selectedAssetId,
        selectedTimeframe,
        DISPLAY_ROWS,
        selectedDerived,
        selectedRange
      );
      setState({ kind: "ready", value });
    } catch (error) {
      setState({ kind: "error", error: asWorkbenchError(error) });
    }
  }

  async function importSampleForWorkbench() {
    if (!profileRoot) return;
    setSampleImport({ kind: "loading" });
    setState({ kind: "loading" });
    setAnalysis({ kind: "idle" });
    setComparison({ kind: "idle" });
    setExportState({ kind: "idle" });
    try {
      const result = await importBundledSample(profileRoot);
      setSampleImport({ kind: "ready", value: result });
      setAssetId("equity:XNAS:AAPL");
      setTimeframe(result.import.timeframe);
      setRangeStart("");
      setRangeEnd("");
      await loadSeries(
        "equity:XNAS:AAPL",
        result.import.timeframe,
        derivedRequest(),
        {}
      );
      if (profileRoot) {
        void searchAssets("", profileRoot)
          .then((catalog) => setAssets({ kind: "ready", assets: catalog.assets }))
          .catch(() => undefined);
      }
    } catch (error) {
      setSampleImport({ kind: "error", message: errorMessage(error) });
      setState({ kind: "error", error: asWorkbenchError(error) });
    }
  }

  async function runAnalysis() {
    if (!profileRoot) return;
    setAnalysis({ kind: "loading" });
    try {
      setAnalysis({
        kind: "ready",
        value: await getQuantitativeAnalysis(
          profileRoot,
          assetId,
          timeframe,
          DISPLAY_ROWS,
          {},
          requestedRange()
        )
      });
    } catch (error) {
      setAnalysis({ kind: "error", message: errorMessage(error) });
    }
  }

  async function runComparison() {
    if (!profileRoot) return;
    setComparison({ kind: "loading" });
    try {
      setComparison({
        kind: "ready",
        value: await getComparison(
          profileRoot,
          assetId,
          comparisonAssetId,
          timeframe,
          20,
          DISPLAY_ROWS,
          requestedRange()
        )
      });
    } catch (error) {
      setComparison({ kind: "error", message: errorMessage(error) });
    }
  }

  async function prepareExport() {
    if (!profileRoot) return;
    setExportState({ kind: "loading" });
    try {
      setExportState({
        kind: "ready",
        value: await prepareWorkbenchExport(
          profileRoot,
          assetId,
          timeframe,
          DISPLAY_ROWS,
          derivedRequest(),
          requestedRange()
        )
      });
    } catch (error) {
      setExportState({ kind: "error", message: errorMessage(error) });
    }
  }

  async function saveNewView() {
    if (!profileRoot || !viewName.trim()) return;
    try {
      const created = await createWorkbenchView(
        profileRoot,
        viewName.trim(),
        "Saved from the D5 desktop workbench",
        currentConfig()
      );
      setActiveViewId(created.view_id);
      setViewName(created.name);
      await refreshViews(profileRoot);
    } catch (error) {
      setViews({ kind: "error", message: errorMessage(error) });
    }
  }

  async function updateActiveView() {
    if (!profileRoot || activeViewId === null) return;
    try {
      await updateWorkbenchView(
        profileRoot,
        activeViewId,
        "Saved from the D5 desktop workbench",
        currentConfig()
      );
      if (viewName.trim()) {
        await renameWorkbenchView(profileRoot, activeViewId, viewName.trim());
      }
      await refreshViews(profileRoot);
    } catch (error) {
      setViews({ kind: "error", message: errorMessage(error) });
    }
  }

  async function removeActiveView() {
    if (!profileRoot || activeViewId === null) return;
    try {
      await deleteWorkbenchView(profileRoot, activeViewId);
      setActiveViewId(null);
      setViewName("");
      await refreshViews(profileRoot);
    } catch (error) {
      setViews({ kind: "error", message: errorMessage(error) });
    }
  }

  function applyView(view: SavedWorkbenchView) {
    const config = view.config;
    const primary = config.primary_asset_id;
    const comparisonId = config.comparison_asset_id;
    const savedTimeframe = config.timeframe;
    const savedRange = config.range;
    const derived = config.derived;
    if (typeof primary === "string") setAssetId(primary);
    if (typeof comparisonId === "string") setComparisonAssetId(comparisonId);
    if (typeof savedTimeframe === "string") setTimeframe(savedTimeframe);
    if (typeof savedRange === "object" && savedRange !== null && !Array.isArray(savedRange)) {
      const range = savedRange as Record<string, unknown>;
      setRangeStart(typeof range.start === "string" ? range.start : "");
      setRangeEnd(typeof range.end === "string" ? range.end : "");
    } else {
      setRangeStart("");
      setRangeEnd("");
    }
    if (Array.isArray(derived) && derived.length === 1 && typeof derived[0] === "object" && derived[0] !== null) {
      const item = derived[0] as Record<string, unknown>;
      if (typeof item.kind === "string" && isDerivedKind(item.kind)) {
        setIndicator(item.kind);
      }
      if (typeof item.window === "number") setWindowSize(item.window);
    } else {
      setIndicator("none");
    }
    setActiveViewId(view.view_id);
    setViewName(view.name);
  }

  if (!profileRoot) {
    return (
      <section className="workbench-empty" role="note">
        <h2>Open a profile to use Workbench</h2>
        <p>Workbench reads governed local, sample, or retained data from an opened profile.</p>
      </section>
    );
  }

  return (
    <section className="workbench-surface" aria-labelledby="workbench-title">
      <header className="workbench-heading">
        <div>
          <p className="workbench-eyebrow">D5 quantitative analysis</p>
          <h2 id="workbench-title">Charting workbench</h2>
          <p>Numerical series, indicators, and comparisons are calculated by Python; this surface renders returned values.</p>
        </div>
        <div className="workbench-boundary" role="note">
          Research only · no recommendations · no broker or real-capital execution
        </div>
      </header>

      <form className="workbench-controls" onSubmit={(event) => void load(event)}>
        <label>
          Asset
          <select value={assetId} onChange={(event) => setAssetId(event.target.value)}>
            {assets.kind === "ready"
              ? assets.assets.map((asset) => (
                  <option key={asset.asset_id} value={asset.asset_id}>
                    {asset.symbol} · {asset.venue} · {asset.name}
                  </option>
                ))
              : <option value={assetId}>Loading asset catalog…</option>}
          </select>
        </label>
        <label>
          Timeframe
          <select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>
            {["1m", "5m", "15m", "30m", "1h", "4h", "1d"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </label>
        <label>
          Indicator
          <select value={indicator} onChange={(event) => setIndicator(event.target.value as typeof indicator)}>
            <option value="none">None</option>
            <option value="simple_return">Simple return</option>
            <option value="log_return">Log return</option>
            <option value="sma">Simple moving average</option>
            <option value="ema">Exponential moving average</option>
            <option value="rolling_volatility">Rolling volatility</option>
            <option value="rolling_volume">Rolling volume</option>
          </select>
        </label>
        <label>
          Window
          <input
            disabled={indicator === "none" || indicator === "simple_return" || indicator === "log_return"}
            min={2}
            max={5000}
            onChange={(event) => setWindowSize(Number(event.target.value))}
            type="number"
            value={windowSize}
          />
        </label>
        <button disabled={state.kind === "loading" || assets.kind !== "ready"} type="submit">
          {state.kind === "loading" ? "Loading…" : "Load governed series"}
        </button>
      </form>

      <section className="workbench-range-controls" aria-labelledby="workbench-range-title">
        <div>
          <h3 id="workbench-range-title">Authoritative data range</h3>
          <p id="workbench-range-help">Optional ISO-8601 timestamps are sent unchanged to Python. Include timezone information.</p>
        </div>
        <label>
          Start
          <input
            aria-describedby="workbench-range-help"
            onChange={(event) => setRangeStart(event.target.value)}
            placeholder="2026-01-01T00:00:00Z"
            type="text"
            value={rangeStart}
          />
        </label>
        <label>
          End
          <input
            aria-describedby="workbench-range-help"
            onChange={(event) => setRangeEnd(event.target.value)}
            placeholder="2026-12-31T23:59:59Z"
            type="text"
            value={rangeEnd}
          />
        </label>
      </section>

      <section className="workbench-secondary-controls" aria-label="Quantitative workbench actions">
        <button disabled={state.kind !== "ready" || analysis.kind === "loading"} onClick={() => void runAnalysis()} type="button">
          {analysis.kind === "loading" ? "Analyzing…" : "Run RSI · ATR · Bollinger · MACD analysis"}
        </button>
        <label>
          Comparison asset
          <select value={comparisonAssetId} onChange={(event) => setComparisonAssetId(event.target.value)}>
            {assets.kind === "ready" ? assets.assets.filter((asset) => asset.asset_id !== assetId).map((asset) => (
              <option key={asset.asset_id} value={asset.asset_id}>{asset.symbol} · {asset.venue}</option>
            )) : null}
          </select>
        </label>
        <button disabled={state.kind !== "ready" || comparison.kind === "loading"} onClick={() => void runComparison()} type="button">
          {comparison.kind === "loading" ? "Comparing…" : "Compare governed returns"}
        </button>
      </section>

      <section className="workbench-saved-views" aria-labelledby="saved-views-title">
        <h3 id="saved-views-title">Saved workbench views</h3>
        <div className="workbench-view-actions">
          <label>View name<input maxLength={80} onChange={(event) => setViewName(event.target.value)} value={viewName} /></label>
          <button disabled={!viewName.trim()} onClick={() => void saveNewView()} type="button">Save new view</button>
          <button disabled={activeViewId === null} onClick={() => void updateActiveView()} type="button">Update active view</button>
          <button disabled={activeViewId === null} onClick={() => void removeActiveView()} type="button">Delete active view</button>
        </div>
        {views.kind === "loading" ? <p role="status">Loading saved views…</p> : null}
        {views.kind === "error" ? <p className="workbench-error" role="alert">{views.message}</p> : null}
        {views.kind === "ready" && views.value.length ? (
          <div className="workbench-view-list">
            {views.value.map((view) => (
              <button aria-pressed={activeViewId === view.view_id} key={view.view_id} onClick={() => applyView(view)} type="button">
                {view.name}
              </button>
            ))}
          </div>
        ) : views.kind === "ready" ? <p>No saved views yet.</p> : null}
      </section>

      {assets.kind === "error" ? <p className="workbench-error" role="alert">{assets.message}</p> : null}
      {state.kind === "idle" ? (
        <p className="workbench-status" role="status">
          Load a retained asset, or import the bundled synthetic AAPL/MSFT samples directly for offline Workbench acceptance.
        </p>
      ) : null}
      {state.kind === "idle" || state.kind === "error" ? (
        <section className="workbench-sample-import" aria-labelledby="workbench-sample-import-title">
          <div>
            <h3 id="workbench-sample-import-title">Offline sample for Workbench</h3>
            <p>Imports deterministic synthetic AAPL/MSFT-labelled daily observations into this profile and loads AAPL 1d without network, credentials, or a provider account.</p>
          </div>
          <button disabled={sampleImport.kind === "loading"} onClick={() => void importSampleForWorkbench()} type="button">
            {sampleImport.kind === "loading" ? "Importing samples…" : "Import bundled synthetic samples"}
          </button>
          {sampleImport.kind === "ready" ? (
            <p role="status">Imported {sampleImport.value.imports.length} synthetic datasets for Workbench: {sampleImport.value.imports.map((item) => `${item.symbol} ${item.timeframe}`).join(", ")}.</p>
          ) : sampleImport.kind === "error" ? (
            <p className="workbench-error" role="alert">{sampleImport.message}</p>
          ) : null}
        </section>
      ) : null}
      {state.kind === "loading" ? <p className="workbench-status" role="status">Loading governed analytical data…</p> : null}
      {state.kind === "error" ? (
        <section className="workbench-error" role="alert">
          <strong>Workbench data unavailable.</strong> {state.error.message}
        </section>
      ) : null}
      {state.kind === "ready" ? (
        <WorkbenchResult
          exportState={exportState}
          onPrepareExport={prepareExport}
          result={state.value}
        />
      ) : null}
      <AnalysisResult state={analysis} />
      <ComparisonPanel state={comparison} />
      <ExportPanel state={exportState} />
    </section>
  );
}

function WorkbenchResult({
  exportState,
  onPrepareExport,
  result
}: {
  exportState: AsyncResult<WorkbenchExport>;
  onPrepareExport: () => Promise<void>;
  result: WorkbenchSeries;
}) {
  const returnedRows = result.series.rows;
  const [viewportSize, setViewportSize] = useState(returnedRows.length);
  const [viewportStart, setViewportStart] = useState(0);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const downsampled = result.series.downsampling_method !== "none";

  useEffect(() => {
    setViewportSize(result.series.rows.length);
    setViewportStart(0);
    setSelectedIndex(0);
  }, [result.series.payload_sha256, result.series.first_timestamp, result.series.last_timestamp]);

  const boundedSize = Math.max(1, Math.min(viewportSize, returnedRows.length || 1));
  const boundedStart = Math.max(0, Math.min(viewportStart, Math.max(0, returnedRows.length - boundedSize)));
  const visibleRows = returnedRows.slice(boundedStart, boundedStart + boundedSize);
  const visibleSelectedIndex = Math.max(0, Math.min(selectedIndex, Math.max(0, visibleRows.length - 1)));
  const step = Math.max(1, Math.floor(boundedSize / 3));

  function resetInspection() {
    setSelectedIndex(0);
  }

  function zoomIn() {
    const nextSize = Math.max(5, Math.floor(boundedSize / 2));
    const center = boundedStart + boundedSize / 2;
    setViewportSize(Math.min(nextSize, returnedRows.length));
    setViewportStart(Math.max(0, Math.floor(center - nextSize / 2)));
    resetInspection();
  }

  function zoomOut() {
    const nextSize = Math.min(returnedRows.length, Math.max(5, boundedSize * 2));
    const center = boundedStart + boundedSize / 2;
    setViewportSize(nextSize);
    setViewportStart(Math.max(0, Math.floor(center - nextSize / 2)));
    resetInspection();
  }

  function pan(delta: number) {
    setViewportStart(Math.max(0, Math.min(boundedStart + delta, returnedRows.length - boundedSize)));
    resetInspection();
  }

  return (
    <div className="workbench-result">
      <dl className="workbench-provenance">
        <div><dt>Canonical asset</dt><dd>{result.asset_id}</dd></div>
        <div><dt>Dataset revision</dt><dd>{result.dataset.dataset_revision_id}</dd></div>
        <div><dt>Source</dt><dd>{result.dataset.source_attribution}</dd></div>
        <div><dt>Timeframe</dt><dd>{result.dataset.timeframe}</dd></div>
        <div><dt>Rows</dt><dd>{result.series.filtered_row_count} filtered / {result.series.returned_row_count} returned</dd></div>
        <div><dt>Display method</dt><dd>{result.series.downsampling_method}</dd></div>
      </dl>
      <p className={downsampled ? "workbench-downsampled" : "workbench-full-resolution"} role="status">
        {downsampled
          ? "Display is downsampled for bounded rendering. Full-resolution analytical data remains authoritative."
          : "All filtered rows fit the current display budget."}
      </p>
      <section className="workbench-export-action" aria-labelledby="workbench-export-action-title">
        <div>
          <h3 id="workbench-export-action-title">Full-resolution evidence export</h3>
          <p>Prepare CSV data and reproduction metadata for the full filtered analytical result, independent of the displayed row budget.</p>
        </div>
        <button disabled={exportState.kind === "loading"} onClick={() => void onPrepareExport()} type="button">
          {exportState.kind === "loading" ? "Exporting…" : "Prepare full-resolution CSV evidence"}
        </button>
      </section>
      <section className="workbench-viewport" aria-label="Presentation viewport controls">
        <p role="status">
          Presentation viewport: rows {returnedRows.length ? boundedStart + 1 : 0}–{boundedStart + visibleRows.length} of {returnedRows.length} returned rows. Zoom and pan do not recalculate analytical values.
        </p>
        <div>
          <button disabled={boundedStart === 0} onClick={() => pan(-step)} type="button">Pan earlier</button>
          <button disabled={boundedSize <= 5} onClick={zoomIn} type="button">Zoom in</button>
          <button disabled={boundedSize >= returnedRows.length} onClick={zoomOut} type="button">Zoom out</button>
          <button disabled={boundedStart + boundedSize >= returnedRows.length} onClick={() => pan(step)} type="button">Pan later</button>
        </div>
      </section>
      <PriceChart
        rows={visibleRows}
        selectedIndex={visibleSelectedIndex}
        onSelectIndex={setSelectedIndex}
      />
      <VolumePane rows={visibleRows} />
      {result.series.derived_evidence.length ? (
        <section className="workbench-evidence" aria-labelledby="indicator-evidence-title">
          <h3 id="indicator-evidence-title">Indicator evidence</h3>
          {result.series.derived_evidence.map((item) => (
            <p key={item.series_id}>
              <strong>{item.series_id}</strong>: warm-up {item.warmup_rows} rows · point-in-time safe {item.point_in_time_safe ? "yes" : "no"}
            </p>
          ))}
        </section>
      ) : null}
      <AccessibleSeriesTable rows={visibleRows} selectedIndex={visibleSelectedIndex} />
    </div>
  );
}

function AnalysisResult({ state }: { state: AsyncResult<QuantitativeAnalysis> }) {
  if (state.kind === "idle" || state.kind === "loading") return null;
  if (state.kind === "error") return <p className="workbench-error" role="alert">{state.message}</p>;
  const latest = state.value.points.at(-1);
  return (
    <section className="workbench-analysis" aria-labelledby="quantitative-title">
      <h3 id="quantitative-title">Authoritative quantitative analysis</h3>
      <p>{state.value.source_point_count} analytical points · {state.value.displayed_point_count} displayed · {state.value.display_method}</p>
      <dl className="workbench-provenance">
        <div><dt>Total return</dt><dd>{formatNullable(state.value.summary.total_return)}</dd></div>
        <div><dt>Annualized volatility</dt><dd>{formatNullable(state.value.summary.annualized_volatility)}</dd></div>
        <div><dt>Maximum drawdown</dt><dd>{formatNullable(state.value.summary.maximum_drawdown)}</dd></div>
        <div><dt>Sharpe ratio</dt><dd>{formatNullable(state.value.summary.sharpe_ratio)}</dd></div>
        <div><dt>Latest RSI</dt><dd>{formatNullable(latest?.rsi ?? null)}</dd></div>
        <div><dt>Latest ATR</dt><dd>{formatNullable(latest?.atr ?? null)}</dd></div>
        <div><dt>Latest MACD</dt><dd>{formatNullable(latest?.macd ?? null)}</dd></div>
        <div><dt>Trend regime</dt><dd>{latest?.trend_regime ?? "—"}</dd></div>
      </dl>
      <p>Point-in-time safe: {state.value.point_in_time_safe ? "yes" : "no"}. Output digest: {state.value.output_digest}</p>
    </section>
  );
}

function ComparisonPanel({ state }: { state: AsyncResult<ComparisonResult> }) {
  if (state.kind === "idle" || state.kind === "loading") return null;
  if (state.kind === "error") return <p className="workbench-error" role="alert">Comparison unavailable: {state.message}</p>;
  return (
    <section className="workbench-analysis" aria-labelledby="comparison-title">
      <h3 id="comparison-title">Governed comparison</h3>
      <p>{state.value.primary.symbol} vs {state.value.comparison.symbol} · {state.value.normalization_basis}</p>
      <dl className="workbench-provenance">
        <div><dt>Aligned returns</dt><dd>{state.value.aligned_return_count}</dd></div>
        <div><dt>Correlation</dt><dd>{formatNullable(state.value.correlation)}</dd></div>
        <div><dt>Beta</dt><dd>{formatNullable(state.value.beta)}</dd></div>
        <div><dt>Rolling window</dt><dd>{state.value.rolling_window}</dd></div>
      </dl>
      <ComparisonTable result={state.value} />
    </section>
  );
}

function ComparisonTable({ result }: { result: ComparisonResult }) {
  return (
    <div className="workbench-table-scroll">
      <table>
        <caption>Aligned authoritative return comparison</caption>
        <thead><tr><th>Timestamp</th><th>{result.primary.symbol}</th><th>{result.comparison.symbol}</th><th>Rolling correlation</th></tr></thead>
        <tbody>{result.points.map((point) => (
          <tr key={point.timestamp}>
            <th scope="row">{point.timestamp}</th>
            <td>{format(point.primary_return)}</td>
            <td>{format(point.benchmark_return)}</td>
            <td>{formatNullable(point.rolling_correlation)}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}

function ExportPanel({ state }: { state: AsyncResult<WorkbenchExport> }) {
  if (state.kind === "idle" || state.kind === "loading") return null;
  if (state.kind === "error") return <p className="workbench-error" role="alert">Export failed: {state.message}</p>;
  return (
    <section className="workbench-analysis" aria-labelledby="export-title">
      <h3 id="export-title">Full-resolution evidence export prepared</h3>
      <p>{state.value.row_count} rows exported. Display downsampling active: {state.value.display_downsampling_was_active ? "yes" : "no"}.</p>
      <p><strong>CSV:</strong> {state.value.csv_path}</p>
      <p><strong>Metadata:</strong> {state.value.metadata_path}</p>
      <p><strong>CSV SHA-256:</strong> {state.value.csv_sha256}</p>
    </section>
  );
}

function PriceChart({
  rows,
  selectedIndex,
  onSelectIndex
}: {
  rows: WorkbenchRow[];
  selectedIndex: number;
  onSelectIndex: (index: number) => void;
}) {
  const geometry = useMemo(() => chartGeometry(rows), [rows]);
  const selectedRow = rows[selectedIndex];
  const selectedCandle = geometry.candles[selectedIndex];
  const summary = rows.length
    ? `Price chart with ${rows.length} visible observations. Use Left and Right Arrow, Home, and End to inspect the synchronized values.`
    : "Price chart contains no observations.";

  function inspect(event: KeyboardEvent<SVGSVGElement>) {
    if (!rows.length) return;
    let nextIndex = selectedIndex;
    if (event.key === "ArrowLeft") nextIndex = Math.max(0, selectedIndex - 1);
    else if (event.key === "ArrowRight") nextIndex = Math.min(rows.length - 1, selectedIndex + 1);
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = rows.length - 1;
    else return;
    event.preventDefault();
    onSelectIndex(nextIndex);
  }

  return (
    <figure className="workbench-chart">
      <figcaption><strong>Price and returned indicator series</strong><span>{summary}</span></figcaption>
      <svg
        aria-describedby="workbench-chart-inspection"
        aria-label={summary}
        className="workbench-svg"
        onKeyDown={inspect}
        role="img"
        tabIndex={rows.length ? 0 : -1}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      >
        {geometry.priceTicks.map((tick) => (
          <g className="chart-scale-tick" key={tick.value}>
            <line className="chart-grid" x1={PRICE_AXIS_PADDING} x2={WIDTH - PADDING} y1={tick.y} y2={tick.y} />
            <text className="chart-axis-label" dominantBaseline="middle" textAnchor="end" x={PRICE_AXIS_PADDING - 8} y={tick.y}>
              {format(tick.value)}
            </text>
          </g>
        ))}
        <line className="chart-axis" x1={PRICE_AXIS_PADDING} x2={PRICE_AXIS_PADDING} y1={PADDING} y2={HEIGHT - PADDING} />
        <line className="chart-axis" x1={PRICE_AXIS_PADDING} x2={WIDTH - PADDING} y1={HEIGHT - PADDING} y2={HEIGHT - PADDING} />
        {geometry.timeTicks.map((tick) => (
          <g className="chart-time-tick" key={tick.timestamp}>
            <line className="chart-axis" x1={tick.x} x2={tick.x} y1={HEIGHT - PADDING} y2={HEIGHT - PADDING + 5} />
            <text className="chart-axis-label chart-time-label" textAnchor={tick.anchor} x={tick.x} y={HEIGHT - 8}>
              {tick.label}
            </text>
          </g>
        ))}
        {geometry.candles.map((item) => (
          <g className={item.direction === "up" ? "chart-up" : "chart-down"} key={item.timestamp}>
            <line x1={item.x} x2={item.x} y1={item.highY} y2={item.lowY} />
            <rect height={Math.max(1, Math.abs(item.closeY - item.openY))} width={item.width} x={item.x - item.width / 2} y={Math.min(item.openY, item.closeY)} />
          </g>
        ))}
        {geometry.derived.map((series) => <polyline className="chart-derived" key={series.id} points={series.points} />)}
        {selectedCandle ? (
          <line
            className="chart-inspection-marker"
            x1={selectedCandle.x}
            x2={selectedCandle.x}
            y1={PADDING}
            y2={HEIGHT - PADDING}
          />
        ) : null}
      </svg>
      <p id="workbench-chart-inspection" role="status">
        {selectedRow ? inspectionSummary(selectedRow) : "No chart observation selected."}
      </p>
    </figure>
  );
}

function VolumePane({ rows }: { rows: WorkbenchRow[] }) {
  const maximum = Math.max(1, ...rows.map((row) => row.volume));
  const plotWidth = WIDTH - PADDING * 2;
  const plotHeight = VOLUME_HEIGHT - PADDING;
  const barWidth = rows.length ? Math.max(1, Math.min(12, (plotWidth / rows.length) * 0.7)) : 1;
  const summary = rows.length
    ? `Volume pane with ${rows.length} visible observations from the same returned rows as the price chart and table.`
    : "Volume pane contains no observations.";
  return (
    <figure className="workbench-chart workbench-volume">
      <figcaption><strong>Volume</strong><span>{summary}</span></figcaption>
      <svg aria-label={summary} className="workbench-volume-svg" role="img" viewBox={`0 0 ${WIDTH} ${VOLUME_HEIGHT}`}>
        {rows.map((row, index) => {
          const x = PADDING + (rows.length === 1 ? plotWidth / 2 : (index * plotWidth) / (rows.length - 1));
          const height = (row.volume / maximum) * plotHeight;
          return <rect className="chart-volume" height={height} key={row.timestamp} width={barWidth} x={x - barWidth / 2} y={VOLUME_HEIGHT - height} />;
        })}
      </svg>
    </figure>
  );
}

function AccessibleSeriesTable({
  rows,
  selectedIndex
}: {
  rows: WorkbenchRow[];
  selectedIndex: number;
}) {
  const derivedKeys = rows.length ? Object.keys(rows[0].derived) : [];
  return (
    <section className="workbench-table-region" aria-labelledby="workbench-table-title" tabIndex={0}>
      <h3 id="workbench-table-title">Synchronized visible values</h3>
      <div className="workbench-table-scroll">
        <table>
          <thead><tr><th>Timestamp</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>{derivedKeys.map((key) => <th key={key}>{key}</th>)}</tr></thead>
          <tbody>{rows.map((row, index) => (
            <tr aria-current={index === selectedIndex ? "true" : undefined} className={index === selectedIndex ? "workbench-selected-row" : undefined} key={row.timestamp}>
              <th scope="row">{row.timestamp}</th>
              <td>{format(row.open)}</td>
              <td>{format(row.high)}</td>
              <td>{format(row.low)}</td>
              <td>{format(row.close)}</td>
              <td>{format(row.volume)}</td>
              {derivedKeys.map((key) => <td key={key}>{row.derived[key] == null ? "—" : format(row.derived[key] as number)}</td>)}
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  );
}

function inspectionSummary(row: WorkbenchRow): string {
  const derived = Object.entries(row.derived)
    .map(([key, value]) => `${key} ${value == null ? "unavailable" : format(value)}`)
    .join(", ");
  return [
    `Selected ${row.timestamp}.`,
    `Open ${format(row.open)}, high ${format(row.high)}, low ${format(row.low)}, close ${format(row.close)}, volume ${format(row.volume)}.`,
    derived ? `Derived: ${derived}.` : ""
  ].filter(Boolean).join(" ");
}

function chartGeometry(rows: WorkbenchRow[]) {
  if (!rows.length) {
    return {
      candles: [],
      derived: [] as Array<{ id: string; points: string }>,
      priceTicks: [] as Array<{ value: number; y: number }>,
      timeTicks: [] as Array<{ anchor: "start" | "middle" | "end"; label: string; timestamp: string; x: number }>
    };
  }
  const values = rows.flatMap((row) => [row.low, row.high, ...Object.values(row.derived).filter((value): value is number => value !== null)]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const span = Math.max(maximum - minimum, 1e-9);
  const plotWidth = WIDTH - PRICE_AXIS_PADDING - PADDING;
  const plotHeight = HEIGHT - PADDING * 2;
  const x = (index: number) => PRICE_AXIS_PADDING + (rows.length === 1 ? plotWidth / 2 : (index * plotWidth) / (rows.length - 1));
  const y = (value: number) => PADDING + ((maximum - value) / span) * plotHeight;
  const width = Math.min(14, Math.max(3, (plotWidth / rows.length) * 0.55));
  const candles = rows.map((row, index) => ({ timestamp: row.timestamp, x: x(index), width, highY: y(row.high), lowY: y(row.low), openY: y(row.open), closeY: y(row.close), direction: row.close >= row.open ? "up" : "down" }));
  const priceTicks = Array.from({ length: 4 }, (_, index) => {
    const value = maximum - (span * index) / 3;
    return { value, y: y(value) };
  });
  const tickIndexes = timeTickIndexes(rows.length);
  const timeLabels = formatTimestampTicks(rows.map((row) => row.timestamp));
  const timeTicks = tickIndexes.map((index, tickPosition) => ({
    anchor: tickPosition === 0 ? "start" as const : tickPosition === tickIndexes.length - 1 ? "end" as const : "middle" as const,
    label: timeLabels[index],
    timestamp: rows[index].timestamp,
    x: x(index)
  }));
  const derived = Object.keys(rows[0].derived).map((id) => ({
    id,
    points: rows.map((row, index) => row.derived[id] == null ? null : `${x(index)},${y(row.derived[id] as number)}`).filter((point): point is string => point !== null).join(" ")
  }));
  return { candles, derived, priceTicks, timeTicks };
}

function timeTickIndexes(rowCount: number): number[] {
  const count = Math.min(4, rowCount);
  if (count <= 1) return rowCount ? [0] : [];
  return Array.from(
    new Set(Array.from({ length: count }, (_, index) => Math.round((index * (rowCount - 1)) / (count - 1))))
  );
}

function formatTimestampTicks(timestamps: string[]): string[] {
  const dates = timestamps.map((timestamp) => new Date(timestamp));
  if (dates.some((date) => Number.isNaN(date.getTime()))) {
    return timestamps.map((timestamp) => timestamp.slice(0, 10));
  }
  const sameDate = dates.every((date) => date.toISOString().slice(0, 10) === dates[0].toISOString().slice(0, 10));
  const sameYear = dates.every((date) => date.getUTCFullYear() === dates[0].getUTCFullYear());
  const formatter = sameDate
    ? new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", timeZone: "UTC" })
    : sameYear
      ? new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", timeZone: "UTC" })
      : new Intl.DateTimeFormat(undefined, { month: "short", year: "numeric", timeZone: "UTC" });
  return dates.map((date) => formatter.format(date));
}

function isDerivedKind(value: string): value is WorkbenchDerivedRequest["kind"] {
  return ["simple_return", "log_return", "sma", "ema", "rolling_volatility", "rolling_volume"].includes(value);
}

function asWorkbenchError(error: unknown): WorkbenchClientError {
  return error instanceof WorkbenchClientError
    ? error
    : new WorkbenchClientError(
        "workbench_unavailable",
        error instanceof Error ? error.message : "Workbench data unavailable.",
        true
      );
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Workbench request failed.";
}

function format(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 6 }).format(value);
}

function formatNullable(value: number | null | undefined): string {
  return value == null ? "—" : format(value);
}
