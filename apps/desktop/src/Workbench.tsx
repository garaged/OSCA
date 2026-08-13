import { FormEvent, useEffect, useMemo, useState } from "react";
import { Asset, searchAssets } from "./marketsApi";
import {
  getWorkbenchSeries,
  WorkbenchClientError,
  WorkbenchDerivedRequest,
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
const PADDING = 28;
const DISPLAY_ROWS = 240;

export function WorkbenchSurface({ profileRoot }: { profileRoot?: string }) {
  const [assets, setAssets] = useState<AssetState>({ kind: "loading" });
  const [assetId, setAssetId] = useState("equity:XNAS:AAPL");
  const [comparisonAssetId, setComparisonAssetId] = useState("equity:XNAS:MSFT");
  const [timeframe, setTimeframe] = useState("1d");
  const [indicator, setIndicator] = useState<WorkbenchDerivedRequest["kind"] | "none">("sma");
  const [windowSize, setWindowSize] = useState(3);
  const [state, setState] = useState<LoadState>({ kind: "idle" });
  const [analysis, setAnalysis] = useState<AsyncResult<QuantitativeAnalysis>>({ kind: "idle" });
  const [comparison, setComparison] = useState<AsyncResult<ComparisonResult>>({ kind: "idle" });
  const [exportState, setExportState] = useState<AsyncResult<WorkbenchExport>>({ kind: "idle" });
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

  function derivedRequest(): WorkbenchDerivedRequest[] {
    if (indicator === "none") return [];
    if (indicator === "simple_return" || indicator === "log_return") {
      return [{ kind: indicator }];
    }
    return [{ kind: indicator, window: windowSize }];
  }

  function currentConfig(): Record<string, unknown> {
    return {
      primary_asset_id: assetId,
      comparison_asset_id: comparisonAssetId,
      timeframe,
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
    if (!profileRoot) return;
    setState({ kind: "loading" });
    setAnalysis({ kind: "idle" });
    setComparison({ kind: "idle" });
    setExportState({ kind: "idle" });
    try {
      const value = await getWorkbenchSeries(
        profileRoot,
        assetId,
        timeframe,
        DISPLAY_ROWS,
        derivedRequest()
      );
      setState({ kind: "ready", value });
    } catch (error) {
      setState({ kind: "error", error: asWorkbenchError(error) });
    }
  }

  async function runAnalysis() {
    if (!profileRoot) return;
    setAnalysis({ kind: "loading" });
    try {
      setAnalysis({
        kind: "ready",
        value: await getQuantitativeAnalysis(profileRoot, assetId, timeframe, DISPLAY_ROWS)
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
          DISPLAY_ROWS
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
          derivedRequest()
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
    const derived = config.derived;
    if (typeof primary === "string") setAssetId(primary);
    if (typeof comparisonId === "string") setComparisonAssetId(comparisonId);
    if (typeof savedTimeframe === "string") setTimeframe(savedTimeframe);
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
        <button disabled={state.kind !== "ready" || exportState.kind === "loading"} onClick={() => void prepareExport()} type="button">
          {exportState.kind === "loading" ? "Exporting…" : "Prepare full-resolution CSV evidence"}
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
          Load a retained asset. The bundled synthetic AAPL sample is supported after import from Workspace.
        </p>
      ) : null}
      {state.kind === "loading" ? <p className="workbench-status" role="status">Loading governed analytical data…</p> : null}
      {state.kind === "error" ? (
        <section className="workbench-error" role="alert">
          <strong>Workbench data unavailable.</strong> {state.error.message}
        </section>
      ) : null}
      {state.kind === "ready" ? <WorkbenchResult result={state.value} /> : null}
      <AnalysisResult state={analysis} />
      <ComparisonPanel state={comparison} />
      <ExportPanel state={exportState} />
    </section>
  );
}

function WorkbenchResult({ result }: { result: WorkbenchSeries }) {
  const downsampled = result.series.downsampling_method !== "none";
  return (
    <div className="workbench-result">
      <dl className="workbench-provenance">
        <div><dt>Canonical asset</dt><dd>{result.asset_id}</dd></div>
        <div><dt>Dataset revision</dt><dd>{result.dataset.dataset_revision_id}</dd></div>
        <div><dt>Source</dt><dd>{result.dataset.source_attribution}</dd></div>
        <div><dt>Timeframe</dt><dd>{result.dataset.timeframe}</dd></div>
        <div><dt>Rows</dt><dd>{result.series.filtered_row_count} filtered / {result.series.returned_row_count} displayed</dd></div>
        <div><dt>Display method</dt><dd>{result.series.downsampling_method}</dd></div>
      </dl>
      <p className={downsampled ? "workbench-downsampled" : "workbench-full-resolution"} role="status">
        {downsampled
          ? "Display is downsampled for bounded rendering. Full-resolution analytical data remains authoritative."
          : "All filtered rows fit the current display budget."}
      </p>
      <PriceChart rows={result.series.rows} />
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
      <AccessibleSeriesTable rows={result.series.rows} />
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
    </section>
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

function PriceChart({ rows }: { rows: WorkbenchRow[] }) {
  const geometry = useMemo(() => chartGeometry(rows), [rows]);
  const summary = rows.length
    ? `Price chart with ${rows.length} displayed observations. Exact displayed values are in the synchronized table.`
    : "Price chart contains no observations.";
  return (
    <figure className="workbench-chart">
      <figcaption><strong>Price and returned indicator series</strong><span>{summary}</span></figcaption>
      <svg aria-label={summary} className="workbench-svg" role="img" viewBox={`0 0 ${WIDTH} ${HEIGHT}`}>
        <line className="chart-axis" x1={PADDING} x2={PADDING} y1={PADDING} y2={HEIGHT - PADDING} />
        <line className="chart-axis" x1={PADDING} x2={WIDTH - PADDING} y1={HEIGHT - PADDING} y2={HEIGHT - PADDING} />
        {geometry.candles.map((item) => (
          <g className={item.direction === "up" ? "chart-up" : "chart-down"} key={item.timestamp}>
            <line x1={item.x} x2={item.x} y1={item.highY} y2={item.lowY} />
            <rect height={Math.max(1, Math.abs(item.closeY - item.openY))} width={item.width} x={item.x - item.width / 2} y={Math.min(item.openY, item.closeY)} />
          </g>
        ))}
        {geometry.derived.map((series) => <polyline className="chart-derived" key={series.id} points={series.points} />)}
      </svg>
    </figure>
  );
}

function AccessibleSeriesTable({ rows }: { rows: WorkbenchRow[] }) {
  const derivedKeys = rows.length ? Object.keys(rows[0].derived) : [];
  return (
    <section className="workbench-table-region" aria-labelledby="workbench-table-title" tabIndex={0}>
      <h3 id="workbench-table-title">Synchronized displayed values</h3>
      <div className="workbench-table-scroll">
        <table>
          <thead><tr><th>Timestamp</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>{derivedKeys.map((key) => <th key={key}>{key}</th>)}</tr></thead>
          <tbody>{rows.map((row) => <tr key={row.timestamp}><th scope="row">{row.timestamp}</th><td>{format(row.open)}</td><td>{format(row.high)}</td><td>{format(row.low)}</td><td>{format(row.close)}</td><td>{format(row.volume)}</td>{derivedKeys.map((key) => <td key={key}>{row.derived[key] == null ? "—" : format(row.derived[key] as number)}</td>)}</tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}

function chartGeometry(rows: WorkbenchRow[]) {
  if (!rows.length) return { candles: [], derived: [] as Array<{ id: string; points: string }> };
  const values = rows.flatMap((row) => [row.low, row.high, ...Object.values(row.derived).filter((value): value is number => value !== null)]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const span = Math.max(maximum - minimum, 1e-9);
  const plotWidth = WIDTH - PADDING * 2;
  const plotHeight = HEIGHT - PADDING * 2;
  const x = (index: number) => PADDING + (rows.length === 1 ? plotWidth / 2 : (index * plotWidth) / (rows.length - 1));
  const y = (value: number) => PADDING + ((maximum - value) / span) * plotHeight;
  const width = Math.min(14, Math.max(3, (plotWidth / rows.length) * 0.55));
  const candles = rows.map((row, index) => ({ timestamp: row.timestamp, x: x(index), width, highY: y(row.high), lowY: y(row.low), openY: y(row.open), closeY: y(row.close), direction: row.close >= row.open ? "up" : "down" }));
  const derived = Object.keys(rows[0].derived).map((id) => ({
    id,
    points: rows.map((row, index) => row.derived[id] == null ? null : `${x(index)},${y(row.derived[id] as number)}`).filter((point): point is string => point !== null).join(" ")
  }));
  return { candles, derived };
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
