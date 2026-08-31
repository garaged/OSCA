import { FormEvent, useEffect, useState } from "react";
import {
  cancelMLExperiment,
  createMLExperiment,
  listMLCatalog,
  listMLExperiments,
  MLCatalog,
  MLExperiment,
  runMLExperiment
} from "./mlLabApi";
import "./mlLab.css";

type LoadState = "idle" | "loading" | "ready" | "error";

export function MLLabSurface({ profileRoot }: { profileRoot?: string }) {
  const [catalog, setCatalog] = useState<MLCatalog | null>(null);
  const [experiments, setExperiments] = useState<MLExperiment[]>([]);
  const [selected, setSelected] = useState<MLExperiment | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [name, setName] = useState("AAPL governed ridge baseline");
  const [assetId, setAssetId] = useState("equity:XNAS:AAPL");
  const [task, setTask] = useState<"regression" | "classification">("regression");
  const [model, setModel] = useState("ridge_regression");
  const [horizon, setHorizon] = useState(1);
  const [window, setWindow] = useState(5);
  const [embargo, setEmbargo] = useState(1);
  const [iterations, setIterations] = useState(500);

  async function reload(selectId?: string) {
    if (!profileRoot) {
      setCatalog(null);
      setExperiments([]);
      setSelected(null);
      return;
    }
    setState("loading");
    try {
      const [nextCatalog, nextExperiments] = await Promise.all([
        listMLCatalog(profileRoot),
        listMLExperiments(profileRoot)
      ]);
      setCatalog(nextCatalog);
      setExperiments(nextExperiments);
      setSelected(
        nextExperiments.find((item) => item.experiment_id === selectId) ??
          nextExperiments.find((item) => item.experiment_id === selected?.experiment_id) ??
          nextExperiments[0] ??
          null
      );
      setState("ready");
    } catch (error) {
      setState("error");
      setFeedback(message(error));
    }
  }

  useEffect(() => {
    void reload();
  }, [profileRoot]);

  function changeTask(next: "regression" | "classification") {
    setTask(next);
    setModel(next === "classification" ? "logistic_classification" : "ridge_regression");
  }

  async function plan(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    setFeedback("Retaining the immutable experiment definition…");
    try {
      const experiment = await createMLExperiment(profileRoot, {
        name,
        assetId,
        timeframe: "1d",
        task,
        model,
        horizon,
        featureWindow: window,
        trainFraction: 0.6,
        validationFraction: 0.2,
        embargo,
        iterations
      });
      setSelected(experiment);
      setFeedback("Experiment planned with immutable dataset and feature lineage.");
      await reload(experiment.experiment_id);
    } catch (error) {
      setFeedback(message(error));
    }
  }

  async function run(experiment: MLExperiment) {
    if (!profileRoot) return;
    setFeedback("Running bounded local experiment…");
    try {
      const result = await runMLExperiment(profileRoot, experiment.experiment_id);
      setSelected(result);
      setFeedback(`Experiment retained as ${result.status}.`);
      await reload(result.experiment_id);
    } catch (error) {
      setFeedback(message(error));
      await reload(experiment.experiment_id);
    }
  }

  async function cancel(experiment: MLExperiment) {
    if (!profileRoot) return;
    try {
      const result = await cancelMLExperiment(profileRoot, experiment.experiment_id);
      setSelected(result);
      setFeedback("Experiment cancelled; no model was promoted or deployed.");
      await reload(result.experiment_id);
    } catch (error) {
      setFeedback(message(error));
    }
  }

  return (
    <section className="ml-lab" aria-labelledby="ml-lab-heading">
      <header className="ml-lab-hero">
        <div>
          <p className="eyebrow">D10 governed ML research</p>
          <h1 id="ml-lab-heading">ML Lab</h1>
          <p>Build point-in-time datasets and compare bounded local models with mandatory simple baselines.</p>
        </div>
        <div className="ml-lab-boundaries" aria-label="ML safety boundary">
          <span>Research evidence only</span>
          <span>Local deterministic inputs</span>
          <span>No automatic promotion</span>
          <span>No recommendation or execution</span>
        </div>
      </header>

      {!profileRoot ? <p className="ml-notice" role="note">Open a validated profile before using ML Lab.</p> : null}
      {feedback ? <p className="ml-notice" role={state === "error" ? "alert" : "status"}>{feedback}</p> : null}

      <div className="ml-grid">
        <section className="ml-panel" aria-labelledby="catalog-heading">
          <h2 id="catalog-heading">Governed feature catalog</h2>
          <p>Every built-in feature uses completed bars only and fails closed on missing inputs.</p>
          {catalog ? (
            <ul className="ml-catalog-list">
              {catalog.features.map((feature) => (
                <li key={feature.feature_id}>
                  <strong>{feature.name}</strong>
                  <code>{feature.feature_id}</code>
                  <span>{feature.transformation}</span>
                  <span>Lookback: {feature.lookback_bars} · Point-in-time safe: yes</span>
                </li>
              ))}
            </ul>
          ) : <p>{state === "loading" ? "Loading catalog…" : "No catalog loaded."}</p>}
        </section>

        <section className="ml-panel" aria-labelledby="builder-heading">
          <h2 id="builder-heading">Dataset and experiment builder</h2>
          <form className="ml-form" onSubmit={(event) => void plan(event)}>
            <label>Name<input value={name} onChange={(event) => setName(event.target.value)} maxLength={100} /></label>
            <label>Governed dataset<select value={assetId} onChange={(event) => setAssetId(event.target.value)}><option value="equity:XNAS:AAPL">AAPL · 1d · newest retained revision</option><option value="equity:XNAS:MSFT">MSFT · 1d · newest retained revision</option></select></label>
            <label>Task<select value={task} onChange={(event) => changeTask(event.target.value as "regression" | "classification")}><option value="regression">Regression</option><option value="classification">Classification</option></select></label>
            <label>Model<select value={model} onChange={(event) => setModel(event.target.value)}>{task === "regression" ? <><option value="ridge_regression">Ridge regression</option><option value="linear_regression">Linear regression</option></> : <option value="logistic_classification">Logistic classification</option>}</select></label>
            <div className="ml-form-row">
              <label>Label horizon<input type="number" min={1} max={252} value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /></label>
              <label>Feature window<input type="number" min={2} max={252} value={window} onChange={(event) => setWindow(Number(event.target.value))} /></label>
              <label>Embargo bars<input type="number" min={0} max={252} value={embargo} onChange={(event) => setEmbargo(Number(event.target.value))} /></label>
              <label>Iterations<input type="number" min={10} max={10000} value={iterations} onChange={(event) => setIterations(Number(event.target.value))} /></label>
            </div>
            <div className="ml-policy" role="note">
              <strong>Fixed safety policies</strong>
              <span>Chronological 60/20/20 split · horizon purge · explicit embargo</span>
              <span>Single-asset survivorship · governed corporate-action semantics · missing data fails closed</span>
            </div>
            <button disabled={!profileRoot || state === "loading"} type="submit">Retain experiment plan</button>
          </form>
        </section>
      </div>

      <section className="ml-panel" aria-labelledby="registry-heading">
        <h2 id="registry-heading">Experiment registry</h2>
        {experiments.length === 0 ? <p>No retained experiments yet.</p> : (
          <div className="ml-table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Status</th><th>Dataset revision</th><th>Actions</th></tr></thead>
              <tbody>{experiments.map((experiment) => <tr key={experiment.experiment_id} data-selected={selected?.experiment_id === experiment.experiment_id}><td><button className="ml-link-button" onClick={() => setSelected(experiment)} type="button">{experiment.name}</button></td><td>{experiment.status}</td><td><code>{definitionText(experiment, "dataset_revision_id")}</code></td><td><div className="ml-actions">{["planned", "failed"].includes(experiment.status) ? <button onClick={() => void run(experiment)} type="button">Run bounded experiment</button> : null}{experiment.status === "planned" ? <button onClick={() => void cancel(experiment)} type="button">Cancel</button> : null}</div></td></tr>)}</tbody>
            </table>
          </div>
        )}
      </section>

      {selected ? <ExperimentEvidence experiment={selected} /> : null}
    </section>
  );
}

function ExperimentEvidence({ experiment }: { experiment: MLExperiment }) {
  const split = objectValue(experiment.definition, "split_policy");
  const result = experiment.result;
  const splits = result ? arrayValue(result, "splits") : [];
  const test = result ? objectValue(result, "test_metrics") : null;
  const baseline = result ? objectValue(result, "baseline_test_metrics") : null;
  return (
    <section className="ml-panel ml-evidence" aria-labelledby="evidence-heading">
      <h2 id="evidence-heading">Reproducible experiment evidence</h2>
      <dl className="ml-evidence-grid">
        <div><dt>Status</dt><dd>{experiment.status}</dd></div>
        <div><dt>Dataset revision</dt><dd><code>{definitionText(experiment, "dataset_revision_id")}</code></dd></div>
        <div><dt>Payload digest</dt><dd><code>{definitionText(experiment, "payload_sha256")}</code></dd></div>
        <div><dt>Output digest</dt><dd><code>{experiment.output_digest ?? "not produced"}</code></dd></div>
        <div><dt>Project pin identity</dt><dd><code>ml-experiment:{experiment.experiment_id}</code></dd></div>
        <div><dt>Split</dt><dd>{split ? `${split.train_fraction}/${split.validation_fraction}/test remainder` : "unavailable"}</dd></div>
        <div><dt>Purge / embargo</dt><dd>{split ? `${split.purge_bars} / ${split.embargo_bars} bars` : "unavailable"}</dd></div>
      </dl>
      {experiment.error ? <p role="alert"><strong>{experiment.error.code}:</strong> {experiment.error.message}</p> : null}
      {splits.length > 0 ? <div className="ml-table-wrap"><table><caption>Chronological partitions</caption><thead><tr><th>Split</th><th>Start</th><th>End</th><th>Rows</th></tr></thead><tbody>{splits.map((item, index) => { const row = asObject(item); return <tr key={index}><td>{String(row.name)}</td><td>{String(row.start)}</td><td>{String(row.end)}</td><td>{String(row.rows)}</td></tr>; })}</tbody></table></div> : null}
      {test && baseline ? <div className="ml-table-wrap"><table><caption>Test evidence versus mandatory baseline</caption><thead><tr><th>Metric</th><th>Model</th><th>Baseline</th></tr></thead><tbody>{metricRows(test, baseline).map((row) => <tr key={row.name}><td>{row.name}</td><td>{row.model}</td><td>{row.baseline}</td></tr>)}</tbody></table></div> : null}
      <p className="ml-policy" role="note">Test metrics remain research evidence. D10 cannot approve, promote, recommend, deploy, or submit orders from this result.</p>
    </section>
  );
}

function definitionText(experiment: MLExperiment, key: string): string {
  const value = experiment.definition[key];
  return typeof value === "string" ? value : "unavailable";
}

function objectValue(row: Record<string, unknown>, key: string): Record<string, unknown> | null {
  const value = row[key];
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function arrayValue(row: Record<string, unknown>, key: string): unknown[] {
  return Array.isArray(row[key]) ? row[key] as unknown[] : [];
}

function asObject(value: unknown): Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function metricRows(model: Record<string, unknown>, baseline: Record<string, unknown>) {
  return Object.keys(model).filter((key) => model[key] != null || baseline[key] != null).map((key) => ({ name: key.replaceAll("_", " "), model: formatMetric(model[key]), baseline: formatMetric(baseline[key]) }));
}

function formatMetric(value: unknown): string {
  return typeof value === "number" ? value.toFixed(6) : "n/a";
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : "ML Lab request failed.";
}
