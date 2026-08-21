import { FormEvent, useEffect, useState } from "react";
import { listPortfolios, VirtualPortfolio } from "./portfolioApi";
import {
  AnalyticsReport,
  BenchmarkComparison,
  captureAnalyticsSnapshot,
  comparePortfolioBenchmark,
  getAnalyticsReport,
  runPortfolioScenario,
  ScenarioReport
} from "./portfolioAnalyticsApi";
import {
  announcePortfolioWorkspaceChange,
  subscribePortfolioWorkspaceChanges
} from "./portfolioWorkspaceEvents";
import "./portfolioAnalytics.css";

export function PortfolioAnalyticsSurface({ profileRoot }: { profileRoot?: string }) {
  const [portfolios, setPortfolios] = useState<VirtualPortfolio[]>([]);
  const [portfolioId, setPortfolioId] = useState("");
  const [report, setReport] = useState<AnalyticsReport | null>(null);
  const [scenario, setScenario] = useState<ScenarioReport | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkComparison | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [assetId, setAssetId] = useState("");
  const [assetShock, setAssetShock] = useState("0.10");
  const [fxCurrency, setFxCurrency] = useState("");
  const [fxShock, setFxShock] = useState("0.05");
  const [benchmarkSource, setBenchmarkSource] = useState("local-benchmark");
  const [benchmarkStart, setBenchmarkStart] = useState("100");
  const [benchmarkEnd, setBenchmarkEnd] = useState("105");

  async function loadReport(targetId: string) {
    if (!profileRoot || !targetId) return;
    try {
      const loaded = await getAnalyticsReport(profileRoot, targetId);
      setReport(loaded);
      if (!assetId && loaded.attribution.items[0]) {
        setAssetId(loaded.attribution.items[0].instrument_id);
      }
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function reload(targetId?: string) {
    if (!profileRoot) {
      setPortfolios([]);
      setPortfolioId("");
      setReport(null);
      return;
    }
    try {
      const listed = await listPortfolios(profileRoot);
      setPortfolios(listed.portfolios);
      const selected =
        listed.portfolios.find((portfolio) => portfolio.portfolio_id === targetId) ??
        listed.portfolios.find((portfolio) => portfolio.portfolio_id === portfolioId) ??
        listed.portfolios[0];
      if (!selected) {
        setPortfolioId("");
        setReport(null);
        return;
      }
      setPortfolioId(selected.portfolio_id);
      await loadReport(selected.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  useEffect(() => {
    void reload();
    return subscribePortfolioWorkspaceChanges("analytics", (detail) => {
      setScenario(null);
      setBenchmark(null);
      void reload(detail.portfolioId);
    });
  }, [profileRoot]);

  async function selectPortfolio(targetId: string) {
    setPortfolioId(targetId);
    setScenario(null);
    setBenchmark(null);
    await loadReport(targetId);
    announcePortfolioWorkspaceChange({
      kind: "selection",
      portfolioId: targetId,
      source: "analytics"
    });
  }

  async function capture() {
    if (!profileRoot || !portfolioId) return;
    try {
      await captureAnalyticsSnapshot(profileRoot, portfolioId);
      setNotice("Complete valuation state captured as immutable analytical evidence.");
      await loadReport(portfolioId);
      announcePortfolioWorkspaceChange({
        kind: "mutation",
        portfolioId,
        source: "analytics"
      });
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitScenario(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !portfolioId) return;
    const assetShocks = assetId.trim() ? { [assetId.trim()]: assetShock } : {};
    const fxShocks = fxCurrency.trim() ? { [fxCurrency.trim().toUpperCase()]: fxShock } : {};
    try {
      setScenario(await runPortfolioScenario(profileRoot, portfolioId, assetShocks, fxShocks));
      setNotice("Scenario calculated from a projection copy; the portfolio was not mutated.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitBenchmark(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !portfolioId || !report?.performance) return;
    try {
      setBenchmark(
        await comparePortfolioBenchmark(profileRoot, portfolioId, [
          {
            observed_at: report.performance.evidence_start,
            value: benchmarkStart,
            source_id: benchmarkSource
          },
          {
            observed_at: report.performance.evidence_end,
            value: benchmarkEnd,
            source_id: benchmarkSource
          }
        ])
      );
      setNotice("Benchmark comparison is descriptive research evidence only.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  return (
    <section className="portfolio-analytics portfolio-lab-panel" aria-labelledby="portfolio-analytics-title">
      <div className="portfolio-lab-heading-row">
        <div>
          <p className="eyebrow">Derived research evidence</p>
          <h2 id="portfolio-analytics-title">Performance, attribution and scenarios</h2>
          <p>
            Analytics are derived from retained accounting and valuation evidence. Benchmark output is descriptive,
            and scenario shocks never write portfolio state.
          </p>
        </div>
        <button disabled={!profileRoot || !portfolioId} onClick={() => void capture()} type="button">
          Capture snapshot
        </button>
      </div>

      {notice ? <p className="portfolio-lab-notice" role="status">{notice}</p> : null}

      <label className="portfolio-analytics-selector">
        Portfolio
        <select
          disabled={!profileRoot || portfolios.length === 0}
          onChange={(event) => void selectPortfolio(event.target.value)}
          value={portfolioId}
        >
          {portfolios.map((portfolio) => (
            <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>{portfolio.name}</option>
          ))}
        </select>
      </label>

      {report ? (
        <>
          <dl className="portfolio-metrics">
            <div><dt>Snapshots</dt><dd>{report.snapshot_count}</dd></div>
            <div><dt>Cumulative return</dt><dd>{report.performance?.cumulative_return ?? "Capture a snapshot"}</dd></div>
            <div><dt>Max drawdown</dt><dd>{report.performance?.max_drawdown ?? "Capture a snapshot"}</dd></div>
            <div><dt>Attribution health</dt><dd>{report.attribution.health}</dd></div>
          </dl>

          {report.performance ? (
            <div className="portfolio-table-wrap">
              <table>
                <caption>Retained portfolio performance snapshots</caption>
                <thead><tr><th>Captured</th><th>Equity</th><th>Return</th><th>Drawdown</th></tr></thead>
                <tbody>
                  {report.performance.points.map((point) => (
                    <tr key={point.snapshot_id}>
                      <td>{point.captured_at}</td><td>{point.equity_base}</td>
                      <td>{point.cumulative_return}</td><td>{point.drawdown}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          <div className="portfolio-table-wrap">
            <table>
              <caption>Current per-asset attribution</caption>
              <thead><tr><th>Instrument</th><th>Market value</th><th>Book cost</th><th>Unrealized P&amp;L</th><th>Allocation</th><th>Source</th></tr></thead>
              <tbody>
                {report.attribution.items.map((item) => (
                  <tr key={item.instrument_id}>
                    <td>{item.instrument_id}</td><td>{item.market_value_base}</td><td>{item.book_cost_base}</td>
                    <td>{item.unrealized_pnl_base}</td><td>{item.allocation}</td>
                    <td>{item.price_source} · {item.price_effective_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="portfolio-lab-layout">
            <section aria-labelledby="portfolio-scenario-title">
              <h3 id="portfolio-scenario-title">Hypothetical shock</h3>
              <form className="portfolio-lab-form" onSubmit={(event) => void submitScenario(event)}>
                <label>Instrument<input value={assetId} onChange={(event) => setAssetId(event.target.value)} /></label>
                <label>Asset shock (decimal)<input inputMode="decimal" value={assetShock} onChange={(event) => setAssetShock(event.target.value)} /></label>
                <label>FX currency (optional)<input maxLength={3} value={fxCurrency} onChange={(event) => setFxCurrency(event.target.value)} /></label>
                <label>FX shock (decimal)<input inputMode="decimal" value={fxShock} onChange={(event) => setFxShock(event.target.value)} /></label>
                <button type="submit">Run scenario</button>
              </form>
              {scenario ? (
                <dl className="portfolio-metrics">
                  <div><dt>Baseline equity</dt><dd>{scenario.baseline_equity}</dd></div>
                  <div><dt>Scenario equity</dt><dd>{scenario.scenario_equity}</dd></div>
                  <div><dt>Equity change</dt><dd>{scenario.equity_change}</dd></div>
                  <div><dt>Portfolio mutated</dt><dd>No</dd></div>
                </dl>
              ) : null}
            </section>

            <section aria-labelledby="portfolio-benchmark-title">
              <h3 id="portfolio-benchmark-title">Descriptive benchmark</h3>
              <form className="portfolio-lab-form" onSubmit={(event) => void submitBenchmark(event)}>
                <label>Source ID<input value={benchmarkSource} onChange={(event) => setBenchmarkSource(event.target.value)} /></label>
                <label>Start value<input inputMode="decimal" value={benchmarkStart} onChange={(event) => setBenchmarkStart(event.target.value)} /></label>
                <label>End value<input inputMode="decimal" value={benchmarkEnd} onChange={(event) => setBenchmarkEnd(event.target.value)} /></label>
                <button disabled={!report.performance} type="submit">Compare benchmark</button>
              </form>
              {benchmark ? (
                <dl className="portfolio-metrics">
                  <div><dt>Portfolio return</dt><dd>{benchmark.portfolio_return}</dd></div>
                  <div><dt>Benchmark return</dt><dd>{benchmark.benchmark_return}</dd></div>
                  <div><dt>Difference</dt><dd>{benchmark.excess_return}</dd></div>
                  <div><dt>Interpretation</dt><dd>Descriptive only</dd></div>
                </dl>
              ) : null}
            </section>
          </div>
        </>
      ) : null}
    </section>
  );
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : "Portfolio analytics operation failed.";
}