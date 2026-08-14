import { FormEvent, KeyboardEvent, useEffect, useMemo, useState } from "react";
import {
  BacktestExport,
  BacktestEvaluation,
  BacktestPoint,
  BacktestResult,
  cancelEvaluation,
  createStrategy,
  createStrategyVersion,
  listStrategies,
  prepareBacktestExport,
  runBacktest,
  runSensitivity,
  runWalkforward,
  StrategyClientError,
  StrategyDefinition,
  validateStrategyDsl,
  ValidationResult
} from "./strategyApi";
import "./strategyLab.css";

type ResultState<T> =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; value: T }
  | { kind: "error"; message: string };

const templateDsl = {
  family: "osca.strategy.dsl",
  version: "1.0.0",
  entry: { type: "close_above_sma", window: 3 },
  exit: { type: "close_below_sma", window: 3 },
  sizing: { type: "fixed_fraction", fraction: 1 },
  risk: { max_position_fraction: 1 },
  costs: { fees_bps: 1, slippage_bps: 2 }
};

export function StrategyLabSurface({ profileRoot }: { profileRoot?: string }) {
  const [strategies, setStrategies] = useState<ResultState<StrategyDefinition[]>>({ kind: "idle" });
  const [active, setActive] = useState<StrategyDefinition | null>(null);
  const [validation, setValidation] = useState<ResultState<ValidationResult>>({ kind: "idle" });
  const [backtest, setBacktest] = useState<ResultState<BacktestResult>>({ kind: "idle" });
  const [evaluation, setEvaluation] = useState<ResultState<BacktestEvaluation>>({ kind: "idle" });
  const [exportState, setExportState] = useState<ResultState<BacktestExport>>({ kind: "idle" });
  const [notice, setNotice] = useState<string | null>(null);
  const [name, setName] = useState("AAPL SMA trend");
  const [entryWindow, setEntryWindow] = useState(3);
  const [exitWindow, setExitWindow] = useState(3);
  const [feesBps, setFeesBps] = useState(1);
  const [slippageBps, setSlippageBps] = useState(2);

  function currentDsl() {
    return {
      ...templateDsl,
      entry: { type: "close_above_sma", window: entryWindow },
      exit: { type: "close_below_sma", window: exitWindow },
      costs: { fees_bps: feesBps, slippage_bps: slippageBps }
    };
  }

  async function reloadStrategies(selectId?: number) {
    if (!profileRoot) {
      setStrategies({ kind: "ready", value: [] });
      setActive(null);
      return;
    }
    setStrategies({ kind: "loading" });
    try {
      const rows = await listStrategies(profileRoot);
      setStrategies({ kind: "ready", value: rows });
      setActive(rows.find((strategy) => strategy.strategy_id === selectId) ?? rows[0] ?? null);
    } catch (error) {
      setStrategies({ kind: "error", message: message(error) });
    }
  }

  useEffect(() => {
    void reloadStrategies();
  }, [profileRoot]);

  async function submitStrategy(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    try {
      const created = await createStrategy(
        profileRoot,
        name,
        "Evaluate a local-only SMA rule with explicit research assumptions.",
        "equity:XNAS:AAPL",
        "1d",
        currentDsl()
      );
      setActive(created);
      setNotice("Strategy created.");
      await reloadStrategies(created.strategy_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function validateCurrent() {
    if (!profileRoot) return;
    setValidation({ kind: "loading" });
    try {
      setValidation({ kind: "ready", value: await validateStrategyDsl(profileRoot, currentDsl()) });
    } catch (error) {
      setValidation({ kind: "error", message: message(error) });
    }
  }

  async function saveVersion() {
    if (!profileRoot || !active) return;
    try {
      const updated = await createStrategyVersion(profileRoot, active.strategy_id, currentDsl(), "Updated guided SMA rule.");
      setActive(updated);
      setNotice("New immutable strategy version saved.");
      await reloadStrategies(updated.strategy_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function runActiveBacktest() {
    if (!profileRoot || !active?.current_version) return;
    setBacktest({ kind: "loading" });
    setExportState({ kind: "idle" });
    setEvaluation({ kind: "idle" });
    try {
      setBacktest({
        kind: "ready",
        value: await runBacktest(profileRoot, active.strategy_id, active.current_version.version_id, 10000)
      });
    } catch (error) {
      setBacktest({ kind: "error", message: message(error) });
    }
  }

  async function exportBacktest() {
    if (!profileRoot || backtest.kind !== "ready") return;
    setExportState({ kind: "loading" });
    try {
      setExportState({
        kind: "ready",
        value: await prepareBacktestExport(profileRoot, backtest.value.result_id)
      });
    } catch (error) {
      setExportState({ kind: "error", message: message(error) });
    }
  }

  async function runSensitivityStudy() {
    if (!profileRoot || !active?.current_version) return;
    setEvaluation({ kind: "loading" });
    try {
      setEvaluation({
        kind: "ready",
        value: await runSensitivity(
          profileRoot,
          active.strategy_id,
          active.current_version.version_id,
          "entry.window",
          [2, entryWindow, Math.min(252, entryWindow + 1)]
        )
      });
    } catch (error) {
      setEvaluation({ kind: "error", message: message(error) });
    }
  }

  async function runWalkforwardStudy() {
    if (!profileRoot || !active?.current_version) return;
    setEvaluation({ kind: "loading" });
    try {
      setEvaluation({
        kind: "ready",
        value: await runWalkforward(profileRoot, active.strategy_id, active.current_version.version_id, 0.5)
      });
    } catch (error) {
      setEvaluation({ kind: "error", message: message(error) });
    }
  }

  async function cancelActiveEvaluation() {
    if (!profileRoot || evaluation.kind !== "ready") return;
    setEvaluation({ kind: "loading" });
    try {
      setEvaluation({
        kind: "ready",
        value: await cancelEvaluation(profileRoot, evaluation.value.evaluation_id)
      });
    } catch (error) {
      setEvaluation({ kind: "error", message: message(error) });
    }
  }

  return (
    <section className="strategy-lab" aria-labelledby="strategy-lab-heading">
      <header className="strategy-lab-hero">
        <div>
          <p className="eyebrow">D7 strategy research</p>
          <h1 id="strategy-lab-heading">Strategy Lab</h1>
          <p>Build guided rule definitions, validate assumptions, and retain research-only backtest evidence.</p>
        </div>
        <div className="strategy-lab-boundaries" aria-label="Strategy lab boundaries">
          <span>Declarative DSL</span>
          <span>Python backtests</span>
          <span>No execution</span>
        </div>
      </header>

      {notice ? <p className="strategy-lab-notice" role="status">{notice}</p> : null}
      {!profileRoot ? (
        <p className="strategy-lab-notice" role="note">Open a validated profile from Workspace before using Strategy Lab.</p>
      ) : null}

      <div className="strategy-lab-layout">
        <section className="strategy-lab-panel" aria-labelledby="strategy-builder-title">
          <h2 id="strategy-builder-title">Guided SMA strategy</h2>
          <form className="strategy-lab-form" onSubmit={(event) => void submitStrategy(event)}>
            <label>Name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
            <label>Entry SMA window<input min="2" max="252" type="number" value={entryWindow} onChange={(event) => setEntryWindow(Number(event.target.value))} /></label>
            <label>Exit SMA window<input min="2" max="252" type="number" value={exitWindow} onChange={(event) => setExitWindow(Number(event.target.value))} /></label>
            <label>Fees bps<input min="0" type="number" value={feesBps} onChange={(event) => setFeesBps(Number(event.target.value))} /></label>
            <label>Slippage bps<input min="0" type="number" value={slippageBps} onChange={(event) => setSlippageBps(Number(event.target.value))} /></label>
            <div className="strategy-lab-actions">
              <button disabled={!profileRoot} type="submit">Create strategy</button>
              <button disabled={!profileRoot} onClick={() => void validateCurrent()} type="button">Validate rules</button>
              <button disabled={!profileRoot || !active} onClick={() => void saveVersion()} type="button">Save new version</button>
            </div>
          </form>
        </section>

        <section className="strategy-lab-panel" aria-labelledby="strategy-list-title">
          <h2 id="strategy-list-title">Strategies</h2>
          {strategies.kind === "loading" ? <p role="status">Loading strategies...</p> : null}
          {strategies.kind === "error" ? <p role="alert">{strategies.message}</p> : null}
          {strategies.kind === "ready" && strategies.value.length === 0 ? <p>No strategies yet.</p> : null}
          <div className="strategy-list">
            {strategies.kind === "ready" ? strategies.value.map((strategy) => (
              <button
                aria-pressed={active?.strategy_id === strategy.strategy_id}
                key={strategy.strategy_id}
                onClick={() => setActive(strategy)}
                type="button"
              >
                <strong>{strategy.name}</strong>
                <span>{strategy.asset_id} · {strategy.timeframe} · {strategy.version_count} version(s)</span>
              </button>
            )) : null}
          </div>
        </section>
      </div>

      <section className="strategy-lab-panel" aria-labelledby="strategy-evidence-title">
        <div className="strategy-lab-heading-row">
          <div>
            <h2 id="strategy-evidence-title">Backtest evidence</h2>
            <p>{active ? `${active.name} · version ${active.current_version?.version_number ?? "n/a"}` : "Select or create a strategy."}</p>
          </div>
          <div className="strategy-lab-actions">
            <button disabled={!profileRoot || !active?.current_version} onClick={() => void runActiveBacktest()} type="button">Run backtest</button>
            <button disabled={!profileRoot || !active?.current_version} onClick={() => void runSensitivityStudy()} type="button">Run sensitivity</button>
            <button disabled={!profileRoot || !active?.current_version} onClick={() => void runWalkforwardStudy()} type="button">Run walk-forward</button>
            <button disabled={evaluation.kind !== "ready"} onClick={() => void cancelActiveEvaluation()} type="button">Cancel evaluation</button>
            <button disabled={backtest.kind !== "ready"} onClick={() => void exportBacktest()} type="button">Export evidence</button>
          </div>
        </div>

        {validation.kind === "ready" ? <ValidationPanel validation={validation.value} /> : null}
        {validation.kind === "error" ? <p role="alert">{validation.message}</p> : null}
        {backtest.kind === "loading" ? <p role="status">Running Python-authoritative backtest...</p> : null}
        {backtest.kind === "error" ? <p role="alert">{backtest.message}</p> : null}
        {backtest.kind === "ready" ? <BacktestPanel result={backtest.value} /> : null}
        {evaluation.kind === "loading" ? <p role="status">Running bounded evaluation...</p> : null}
        {evaluation.kind === "error" ? <p role="alert">{evaluation.message}</p> : null}
        {evaluation.kind === "ready" ? <EvaluationPanel evaluation={evaluation.value} /> : null}
        {exportState.kind === "ready" ? (
          <p className="strategy-lab-export">
            Manifest: {exportState.value.manifest_path}<br />
            Result tables: {exportState.value.data_paths.join(", ")}
          </p>
        ) : null}
        {exportState.kind === "error" ? <p role="alert">{exportState.message}</p> : null}
      </section>
    </section>
  );
}

function ValidationPanel({ validation }: { validation: ValidationResult }) {
  return (
    <div className="strategy-lab-validation">
      <strong>{validation.can_execute ? "Validation passed." : "Validation blocked execution."}</strong>
      {validation.findings.length ? (
        <ul>{validation.findings.map((finding) => <li key={finding.code}>{finding.code}: {finding.message}</li>)}</ul>
      ) : <p>No validation findings.</p>}
    </div>
  );
}

function EvaluationPanel({ evaluation }: { evaluation: BacktestEvaluation }) {
  return (
    <section className="strategy-evaluation" aria-labelledby="strategy-evaluation-title">
      <div className="strategy-lab-heading-row">
        <div>
          <h3 id="strategy-evaluation-title">{evaluation.evaluation_type} evaluation</h3>
          <p>Status {evaluation.status}; digest {evaluation.result_digest}</p>
        </div>
        <p>Evidence: {evaluation.evidence_path}</p>
      </div>
      <dl className="strategy-evaluation-budget">
        {Object.entries(evaluation.budget).map(([key, value]) => (
          <Metric key={key} label={humanize(key)} value={String(value)} />
        ))}
      </dl>
      <p>Budget and cancellation behavior are retained with the evaluation evidence.</p>
      {evaluation.partitions?.length ? (
        <div className="strategy-evaluation-table" role="region" aria-label="Walk-forward train and test partitions">
          <table>
            <thead><tr>{Object.keys(evaluation.partitions[0]).map((key) => <th key={key}>{humanize(key)}</th>)}</tr></thead>
            <tbody>
              {evaluation.partitions.map((row, index) => (
                <tr key={index}>{Object.values(row).map((value, cell) => <td key={cell}>{String(value)}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <div className="strategy-evaluation-table" role="region" aria-label="Evaluation result rows">
        <table>
          <thead><tr>{evaluation.rows.length ? Object.keys(flattenRow(evaluation.rows[0])).map((key) => <th key={key}>{humanize(key)}</th>) : null}</tr></thead>
          <tbody>
            {evaluation.rows.map((row, index) => {
              const flattened = flattenRow(row);
              return <tr key={index}>{Object.values(flattened).map((value, cell) => <td key={cell}>{String(value)}</td>)}</tr>;
            })}
          </tbody>
        </table>
      </div>
      <ul>{evaluation.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
    </section>
  );
}

function BacktestPanel({ result }: { result: BacktestResult }) {
  const [selectedIndex, setSelectedIndex] = useState(Math.max(0, result.equity_curve.length - 1));
  const selected = result.equity_curve[selectedIndex] ?? result.equity_curve[0];

  useEffect(() => {
    setSelectedIndex(Math.max(0, result.equity_curve.length - 1));
  }, [result.result_id, result.equity_curve.length]);

  return (
    <>
      <dl className="strategy-result-grid">
        <Metric label="Final equity" value={currency(result.metrics.final_equity)} />
        <Metric label="Strategy return" value={percent(result.metrics.strategy_return)} />
        <Metric label="Buy and hold" value={percent(result.metrics.buy_and_hold_return)} />
        <Metric label="Max drawdown" value={percent(result.metrics.max_drawdown)} />
        <Metric label="Trades" value={String(result.metrics.trade_count)} />
        <Metric label="Bars" value={String(result.metrics.bars_processed)} />
        <Metric label="Fees" value={`${result.assumptions.fees_bps} bps`} />
        <Metric label="Slippage" value={`${result.assumptions.slippage_bps} bps`} />
      </dl>
      <BacktestCurve
        points={result.equity_curve}
        selectedIndex={selectedIndex}
        setSelectedIndex={setSelectedIndex}
      />
      {selected ? <SelectedObservation point={selected} index={selectedIndex} total={result.equity_curve.length} /> : null}
      <p className="strategy-lab-evidence">Evidence: {result.evidence_path}</p>
      <p className="strategy-lab-evidence">Digest: {result.result_digest}</p>
    </>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}

function BacktestCurve({
  points,
  selectedIndex,
  setSelectedIndex
}: {
  points: BacktestPoint[];
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
}) {
  const plot = useMemo(() => buildPlot(points), [points]);
  const selected = plot.points[selectedIndex] ?? plot.points[0];

  function handleKeyDown(event: KeyboardEvent<SVGSVGElement>) {
    if (!points.length) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      setSelectedIndex(Math.max(0, selectedIndex - 1));
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      setSelectedIndex(Math.min(points.length - 1, selectedIndex + 1));
    } else if (event.key === "Home") {
      event.preventDefault();
      setSelectedIndex(0);
    } else if (event.key === "End") {
      event.preventDefault();
      setSelectedIndex(points.length - 1);
    }
  }

  if (points.length === 0) {
    return <p className="strategy-lab-notice">No result observations were returned.</p>;
  }

  return (
    <figure className="strategy-chart">
      <figcaption>
        Equity curve with {points.length} observations. Use Left and Right Arrow, Home, End, or click a point to inspect synchronized values.
      </figcaption>
      <svg
        aria-label={`Backtest equity chart. Selected ${selected?.label ?? "observation unavailable"}.`}
        className="strategy-chart-svg"
        focusable="true"
        onKeyDown={handleKeyDown}
        role="img"
        tabIndex={0}
        viewBox="0 0 640 280"
      >
        <line className="strategy-axis" x1="56" x2="600" y1="226" y2="226" />
        <line className="strategy-axis" x1="56" x2="56" y1="28" y2="226" />
        {plot.yTicks.map((tick) => (
          <g key={tick.value}>
            <line className="strategy-gridline" x1="56" x2="600" y1={tick.y} y2={tick.y} />
            <text className="strategy-axis-label" x="48" y={tick.y + 4} textAnchor="end">{currency(tick.value)}</text>
          </g>
        ))}
        {plot.xTicks.map((tick) => (
          <g key={`${tick.index}-${tick.label}`}>
            <line className="strategy-tick" x1={tick.x} x2={tick.x} y1="226" y2="232" />
            <text className="strategy-axis-label" x={tick.x} y="250" textAnchor="middle">{tick.label}</text>
          </g>
        ))}
        <polyline className="strategy-equity-line" points={plot.polyline} />
        {plot.points.map((point, index) => (
          <circle
            aria-label={`Select observation ${index + 1}: ${point.label}, equity ${currency(point.equity)}`}
            className={index === selectedIndex ? "strategy-point strategy-point-selected" : "strategy-point"}
            key={`${point.timestamp}-${index}`}
            onClick={() => setSelectedIndex(index)}
            role="button"
            tabIndex={-1}
            cx={point.x}
            cy={point.y}
            r={index === selectedIndex ? 6 : 4}
          />
        ))}
        {selected ? (
          <g aria-hidden="true">
            <line className="strategy-marker" x1={selected.x} x2={selected.x} y1="28" y2="226" />
            <circle className="strategy-marker-point" cx={selected.x} cy={selected.y} r="8" />
          </g>
        ) : null}
      </svg>
    </figure>
  );
}

function SelectedObservation({ point, index, total }: { point: BacktestPoint; index: number; total: number }) {
  return (
    <section className="strategy-selected" aria-labelledby="strategy-selected-title">
      <h3 id="strategy-selected-title">Selected observation {index + 1} of {total}</h3>
      <dl>
        <Metric label="Timestamp" value={point.timestamp} />
        <Metric label="Close" value={currency(point.close)} />
        <Metric label="Equity" value={currency(point.equity)} />
        <Metric label="Drawdown" value={percent(point.drawdown)} />
        <Metric label="Signal" value={point.signal} />
      </dl>
    </section>
  );
}

function buildPlot(points: BacktestPoint[]) {
  const width = 544;
  const height = 198;
  const left = 56;
  const top = 28;
  const bottom = 226;
  const values = points.map((point) => point.equity);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const padding = Math.max((max - min) * 0.08, max * 0.002, 1);
  const yMin = min - padding;
  const yMax = max + padding;
  const denominator = Math.max(1, points.length - 1);
  const scaleY = (value: number) => bottom - ((value - yMin) / (yMax - yMin)) * height;
  const scaled = points.map((point, index) => {
    const x = left + (index / denominator) * width;
    return {
      ...point,
      x,
      y: scaleY(point.equity),
      label: compactDate(point.timestamp)
    };
  });
  const tickValues = [yMin, yMin + (yMax - yMin) / 2, yMax];
  return {
    points: scaled,
    polyline: scaled.map((point) => `${point.x},${point.y}`).join(" "),
    yTicks: tickValues.map((value) => ({ value, y: scaleY(value) })),
    xTicks: smartXTicks(points).map((tick) => ({
      ...tick,
      x: left + (tick.index / denominator) * width
    }))
  };
}

function smartXTicks(points: BacktestPoint[]) {
  if (points.length <= 1) return points.map((point, index) => ({ index, label: compactDate(point.timestamp) }));
  const candidateIndexes = [0, Math.floor((points.length - 1) / 2), points.length - 1];
  const unique = Array.from(new Set(candidateIndexes));
  return unique.map((index) => ({ index, label: compactDate(points[index].timestamp) }));
}

function compactDate(timestamp: string): string {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return timestamp.slice(0, 10);
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(date);
}

function flattenRow(row: Record<string, unknown>): Record<string, string | number | boolean> {
  const metrics = row.metrics && typeof row.metrics === "object" && !Array.isArray(row.metrics)
    ? row.metrics as Record<string, unknown>
    : {};
  const flattened: Record<string, string | number | boolean> = {};
  for (const [key, value] of Object.entries(row)) {
    if (key !== "metrics" && (typeof value === "string" || typeof value === "number" || typeof value === "boolean")) {
      flattened[key] = value;
    }
  }
  for (const key of ["final_equity", "strategy_return", "max_drawdown", "trade_count"]) {
    const value = metrics[key];
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      flattened[key] = value;
    }
  }
  return flattened;
}

function humanize(value: string): string {
  return value.replaceAll("_", " ");
}

function message(error: unknown): string {
  if (error instanceof StrategyClientError) return error.message;
  return error instanceof Error ? error.message : "Strategy Lab request failed.";
}

function currency(value: number): string {
  return new Intl.NumberFormat("en-US", { currency: "USD", style: "currency" }).format(value);
}

function percent(value: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2, style: "percent" }).format(value);
}
