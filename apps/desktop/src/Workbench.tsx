import { FormEvent, useEffect, useMemo, useState } from "react";
import { Asset, searchAssets } from "./marketsApi";
import {
  getWorkbenchSeries,
  WorkbenchClientError,
  WorkbenchDerivedRequest,
  WorkbenchRow,
  WorkbenchSeries
} from "./workbenchApi";
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

const WIDTH = 900;
const HEIGHT = 360;
const PADDING = 28;

export function WorkbenchSurface({ profileRoot }: { profileRoot?: string }) {
  const [assets, setAssets] = useState<AssetState>({ kind: "loading" });
  const [assetId, setAssetId] = useState("equity:XNAS:AAPL");
  const [timeframe, setTimeframe] = useState("1d");
  const [indicator, setIndicator] = useState<"none" | "sma" | "ema">("sma");
  const [windowSize, setWindowSize] = useState(3);
  const [state, setState] = useState<LoadState>({ kind: "idle" });

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

  async function load(event?: FormEvent) {
    event?.preventDefault();
    if (!profileRoot) return;
    setState({ kind: "loading" });
    const derived: WorkbenchDerivedRequest[] =
      indicator === "none" ? [] : [{ kind: indicator, window: windowSize }];
    try {
      const value = await getWorkbenchSeries(profileRoot, assetId, timeframe, 240, derived);
      setState({ kind: "ready", value });
    } catch (error) {
      setState({
        kind: "error",
        error:
          error instanceof WorkbenchClientError
            ? error
            : new WorkbenchClientError(
                "workbench_unavailable",
                error instanceof Error ? error.message : "Workbench data unavailable.",
                true
              )
      });
    }
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
          <p>Numerical series and indicators are calculated by Python; this surface renders returned values.</p>
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
          <select
            value={indicator}
            onChange={(event) => setIndicator(event.target.value as "none" | "sma" | "ema")}
          >
            <option value="none">None</option>
            <option value="sma">Simple moving average</option>
            <option value="ema">Exponential moving average</option>
          </select>
        </label>
        <label>
          Window
          <input
            disabled={indicator === "none"}
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

function format(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 6 }).format(value);
}
