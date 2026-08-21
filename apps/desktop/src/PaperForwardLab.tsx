import { FormEvent, useEffect, useMemo, useState } from "react";
import { DesktopClientError } from "./api";
import { listPortfolios, VirtualPortfolio } from "./portfolioApi";
import {
  appendPaperMark,
  bindPaperRun,
  buildPaperComparison,
  cancelPaperOrder,
  confirmPaperDraft,
  inspectPaperRun,
  PaperBarInput,
  PaperDraftInput,
  PaperOrderRow,
  PaperRunInspection,
  processPaperBar,
  recordPaperCheckpoint,
  retainPaperAssumptions,
  retainPaperDraft
} from "./paperForwardApi";
import "./paperForwardLab.css";

type Props = { profileRoot?: string };
type Feedback = { kind: "success" | "error"; message: string } | null;

const nowIso = () => new Date().toISOString();
const nextHourIso = () => new Date(Date.now() + 60 * 60 * 1000).toISOString();

function newBar(): PaperBarInput {
  return {
    evidenceId: crypto.randomUUID(),
    instrumentId: "equity:XNAS:AAPL",
    datasetRevisionId: crypto.randomUUID(),
    marketSourceId: "local-paper-lab",
    timeframe: "1h",
    barStartedAt: nowIso(),
    barEndedAt: nextHourIso(),
    availableAt: new Date(Date.now() + 60 * 60 * 1000 + 1000).toISOString(),
    open: "100",
    high: "102",
    low: "99",
    close: "101",
    volume: "1000",
    complete: true,
    marketCalendarId: "XNAS",
    sessionOpen: true
  };
}

export function PaperForwardLabSurface({ profileRoot }: Props) {
  const [portfolios, setPortfolios] = useState<VirtualPortfolio[]>([]);
  const [portfolioId, setPortfolioId] = useState("");
  const [paperRunId, setPaperRunId] = useState(() => crypto.randomUUID());
  const [paperAccountId, setPaperAccountId] = useState(() => crypto.randomUUID());
  const [assumptionId, setAssumptionId] = useState(() => crypto.randomUUID());
  const [inspection, setInspection] = useState<PaperRunInspection | null>(null);
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [busy, setBusy] = useState(false);

  const [spreadBps, setSpreadBps] = useState("0");
  const [slippageBps, setSlippageBps] = useState("0");
  const [feeBps, setFeeBps] = useState("0");
  const [flatFee, setFlatFee] = useState("0");
  const [latencyMs, setLatencyMs] = useState(0);
  const [maxVolumeParticipation, setMaxVolumeParticipation] = useState("1");
  const [maxOrderNotional, setMaxOrderNotional] = useState("");
  const [maxPositionNotional, setMaxPositionNotional] = useState("");

  const [draftId, setDraftId] = useState(() => crypto.randomUUID());
  const [draftVersion, setDraftVersion] = useState(1);
  const [instrumentId, setInstrumentId] = useState("equity:XNAS:AAPL");
  const [timeframe, setTimeframe] = useState("1h");
  const [currency, setCurrency] = useState("USD");
  const [datasetRevisionId, setDatasetRevisionId] = useState(() => crypto.randomUUID());
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<
    "market" | "limit" | "stop" | "scheduled_market"
  >("market");
  const [quantity, setQuantity] = useState("10");
  const [limitPrice, setLimitPrice] = useState("");
  const [stopPrice, setStopPrice] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [lotAllocationsText, setLotAllocationsText] = useState("");

  const [selectedOrderId, setSelectedOrderId] = useState("");
  const [bar, setBar] = useState<PaperBarInput>(() => newBar());

  const [backtestResultId, setBacktestResultId] = useState(1);
  const [strategyVersionId, setStrategyVersionId] = useState(1);
  const [backtestStart, setBacktestStart] = useState("2026-01-01T00:00:00Z");
  const [backtestEnd, setBacktestEnd] = useState("2026-06-01T00:00:00Z");
  const [forwardStart, setForwardStart] = useState("2026-08-01T00:00:00Z");
  const [forwardEnd, setForwardEnd] = useState("2026-08-20T00:00:00Z");
  const [metricName, setMetricName] = useState("return");
  const [backtestMetric, setBacktestMetric] = useState("0.10");
  const [forwardMetric, setForwardMetric] = useState("0.04");
  const [comparisonResult, setComparisonResult] = useState<Record<string, unknown> | null>(null);

  const selectedOrder = useMemo(
    () => inspection?.orders.find((item) => item.order.order_id === selectedOrderId) ?? null,
    [inspection, selectedOrderId]
  );

  useEffect(() => {
    if (!profileRoot) {
      setPortfolios([]);
      setPortfolioId("");
      return;
    }
    let active = true;
    void listPortfolios(profileRoot)
      .then((result) => {
        if (!active) return;
        setPortfolios(result.portfolios);
        setPortfolioId((current) => current || result.portfolios[0]?.portfolio_id || "");
      })
      .catch((error) => {
        if (active) setFeedback({ kind: "error", message: errorMessage(error) });
      });
    return () => {
      active = false;
    };
  }, [profileRoot]);

  async function refresh() {
    if (!profileRoot || !paperRunId) return;
    const result = await inspectPaperRun(profileRoot, paperRunId);
    setInspection(result);
    if (!selectedOrderId && result.orders[0]) setSelectedOrderId(result.orders[0].order.order_id);
  }

  async function perform(action: () => Promise<void>, success: string) {
    setBusy(true);
    setFeedback(null);
    try {
      await action();
      setFeedback({ kind: "success", message: success });
    } catch (error) {
      setFeedback({ kind: "error", message: errorMessage(error) });
    } finally {
      setBusy(false);
    }
  }

  async function setupRun(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !portfolioId) return;
    await perform(async () => {
      await bindPaperRun(profileRoot, paperRunId, paperAccountId, portfolioId);
      await retainPaperAssumptions(profileRoot, {
        assumptionId,
        spreadBps,
        slippageBps,
        feeBps,
        flatFee,
        latencyMs,
        maxVolumeParticipation,
        ...(maxOrderNotional ? { maxOrderNotional } : {}),
        ...(maxPositionNotional ? { maxPositionNotional } : {})
      });
      await refresh();
    }, "Simulated paper run and execution assumptions retained.");
  }

  async function saveDraft(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !portfolioId) return;
    await perform(async () => {
      const input: PaperDraftInput = {
        draftId,
        draftVersion,
        paperRunId,
        paperAccountId,
        portfolioId,
        sourceId: `paper-lab:${draftId}:${draftVersion}`,
        instrumentId,
        timeframe,
        currency,
        datasetRevisionId,
        side,
        orderType,
        quantity,
        assumptionId,
        ...(limitPrice ? { limitPrice } : {}),
        ...(stopPrice ? { stopPrice } : {}),
        ...(scheduledAt ? { scheduledAt } : {}),
        ...(expiresAt ? { expiresAt } : {}),
        ...(lotAllocationsText ? { lotAllocations: parseLotAllocations(lotAllocationsText) } : {})
      };
      await retainPaperDraft(profileRoot, input);
      await refresh();
    }, `Draft v${draftVersion} retained. It is not active until explicitly confirmed.`);
  }

  async function confirmDraft() {
    if (!profileRoot) return;
    await perform(async () => {
      const result = await confirmPaperDraft(profileRoot, paperRunId, draftId, draftVersion);
      setSelectedOrderId(result.order.order_id);
      await refresh();
    }, "SIMULATED-ONLY order confirmed. No external destination exists.");
  }

  async function processBar(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !selectedOrderId) return;
    await perform(async () => {
      await processPaperBar(profileRoot, paperRunId, paperAccountId, selectedOrderId, bar);
      await refresh();
    }, "Governed bar processed through the deterministic simulator.");
  }

  async function appendMark() {
    if (!profileRoot || !portfolioId) return;
    await perform(async () => {
      await appendPaperMark(profileRoot, portfolioId, currency, bar);
      await refresh();
    }, "Completed-bar close retained as separate valuation evidence.");
  }

  async function checkpoint() {
    if (!profileRoot) return;
    await perform(async () => {
      await recordPaperCheckpoint(profileRoot, paperRunId, bar);
      await refresh();
    }, "Replay-safe checkpoint retained.");
  }

  async function cancelOrder(row: PaperOrderRow) {
    if (!profileRoot) return;
    await perform(async () => {
      await cancelPaperOrder(profileRoot, row.order.order_id, "cancelled from Paper Lab");
      await refresh();
    }, "Simulated order cancelled.");
  }

  async function compare(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    await perform(async () => {
      const result = await buildPaperComparison(profileRoot, {
        backtestResultId,
        paperRunId,
        strategyVersionId,
        assumptionId,
        backtestStartedAt: backtestStart,
        backtestEndedAt: backtestEnd,
        forwardStartedAt: forwardStart,
        forwardEndedAt: forwardEnd,
        metrics: [
          {
            name: metricName,
            backtestValue: backtestMetric,
            forwardValue: forwardMetric,
            unit: "ratio",
            methodology: "retained window metric supplied for descriptive comparison"
          }
        ],
        methodologyDifferences: [
          "historical backtest and forward paper evaluation windows are distinct",
          "paper fills include the retained D9 execution-assumption revision"
        ]
      });
      setComparisonResult(result);
    }, "Descriptive comparison built. It is not an investment recommendation.");
  }

  function startNewDraftVersion() {
    setDraftVersion((value) => value + 1);
  }

  function startNewRun() {
    setPaperRunId(crypto.randomUUID());
    setPaperAccountId(crypto.randomUUID());
    setAssumptionId(crypto.randomUUID());
    setDraftId(crypto.randomUUID());
    setDraftVersion(1);
    setInspection(null);
    setSelectedOrderId("");
    setComparisonResult(null);
    setFeedback(null);
  }

  if (!profileRoot) {
    return (
      <section className="paper-lab" aria-labelledby="paper-lab-title">
        <h2 id="paper-lab-title">Paper Lab</h2>
        <p>Open and own a validated profile before using simulated paper evaluation.</p>
      </section>
    );
  }

  return (
    <section className="paper-lab" aria-labelledby="paper-lab-title">
      <header className="paper-lab-header">
        <div>
          <p className="paper-lab-eyebrow">D9 · research evidence only</p>
          <h2 id="paper-lab-title">Paper Lab</h2>
          <p>
            Simulated orders use local governed evidence and D8 virtual-portfolio accounting.
            There is no broker, exchange destination, live order API, or real-capital path.
          </p>
        </div>
        <button disabled={busy} onClick={startNewRun} type="button">
          New simulated run
        </button>
      </header>

      <aside className="paper-lab-safety" role="note" aria-label="Simulation safety boundary">
        <strong>SIMULATED ONLY</strong>
        <span>Confirmation activates research simulation only. It cannot submit an external order.</span>
      </aside>

      {feedback ? (
        <p className={`paper-lab-feedback ${feedback.kind}`} role={feedback.kind === "error" ? "alert" : "status"}>
          {feedback.message}
        </p>
      ) : null}

      <form className="paper-lab-card" onSubmit={(event) => void setupRun(event)}>
        <div className="paper-lab-card-heading">
          <h3>1. Run and execution assumptions</h3>
          <span>Immutable evidence</span>
        </div>
        <div className="paper-lab-grid">
          <label>
            Virtual portfolio
            <select value={portfolioId} onChange={(event) => setPortfolioId(event.target.value)} required>
              <option value="">Select portfolio</option>
              {portfolios.map((portfolio) => (
                <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>
                  {portfolio.name} · {portfolio.base_currency}
                </option>
              ))}
            </select>
          </label>
          <ReadOnlyField label="Paper run ID" value={paperRunId} />
          <ReadOnlyField label="Paper account ID" value={paperAccountId} />
          <ReadOnlyField label="Assumption ID" value={assumptionId} />
          <TextField label="Spread (bps)" value={spreadBps} onChange={setSpreadBps} />
          <TextField label="Slippage (bps)" value={slippageBps} onChange={setSlippageBps} />
          <TextField label="Fee (bps)" value={feeBps} onChange={setFeeBps} />
          <TextField label="Flat fee" value={flatFee} onChange={setFlatFee} />
          <label>
            Latency (ms)
            <input min={0} onChange={(event) => setLatencyMs(Number(event.target.value))} type="number" value={latencyMs} />
          </label>
          <TextField
            label="Max volume participation"
            value={maxVolumeParticipation}
            onChange={setMaxVolumeParticipation}
          />
          <TextField label="Max order notional (optional)" value={maxOrderNotional} onChange={setMaxOrderNotional} required={false} />
          <TextField label="Max position notional (optional)" value={maxPositionNotional} onChange={setMaxPositionNotional} required={false} />
        </div>
        <button disabled={busy || !portfolioId} type="submit">Retain run + assumptions</button>
      </form>

      <form className="paper-lab-card" onSubmit={(event) => void saveDraft(event)}>
        <div className="paper-lab-card-heading">
          <h3>2. Immutable simulated-order draft</h3>
          <button disabled={busy} onClick={startNewDraftVersion} type="button">New draft version</button>
        </div>
        <div className="paper-lab-grid">
          <ReadOnlyField label="Draft ID" value={draftId} />
          <ReadOnlyField label="Version" value={String(draftVersion)} />
          <TextField label="Instrument ID" value={instrumentId} onChange={setInstrumentId} />
          <TextField label="Timeframe" value={timeframe} onChange={setTimeframe} />
          <TextField label="Currency" value={currency} onChange={setCurrency} />
          <TextField label="Dataset revision UUID" value={datasetRevisionId} onChange={setDatasetRevisionId} />
          <label>
            Side
            <select value={side} onChange={(event) => setSide(event.target.value as "buy" | "sell")}>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </label>
          <label>
            Simulated order type
            <select value={orderType} onChange={(event) => setOrderType(event.target.value as typeof orderType)}>
              <option value="market">Market</option>
              <option value="limit">Limit</option>
              <option value="stop">Stop</option>
              <option value="scheduled_market">Scheduled market</option>
            </select>
          </label>
          <TextField label="Quantity" value={quantity} onChange={setQuantity} />
          <TextField label="Limit price" value={limitPrice} onChange={setLimitPrice} required={false} disabled={orderType !== "limit"} />
          <TextField label="Stop price" value={stopPrice} onChange={setStopPrice} required={false} disabled={orderType !== "stop"} />
          <TextField label="Scheduled at (ISO-8601)" value={scheduledAt} onChange={setScheduledAt} required={false} disabled={orderType !== "scheduled_market"} />
          <TextField label="Expires at (optional ISO-8601)" value={expiresAt} onChange={setExpiresAt} required={false} />
          <TextField
            label="Sell lot allocations (lot UUID=quantity, comma separated)"
            value={lotAllocationsText}
            onChange={setLotAllocationsText}
            required={false}
            disabled={side !== "sell"}
          />
        </div>
        <div className="paper-lab-actions">
          <button disabled={busy || !inspection} type="submit">Retain draft v{draftVersion}</button>
          <button
            className="paper-lab-confirm"
            disabled={busy || !inspection?.drafts.some((item) => item.draft_id === draftId && item.draft_version === draftVersion)}
            onClick={() => void confirmDraft()}
            type="button"
          >
            Confirm SIMULATED-ONLY order
          </button>
        </div>
      </form>

      <section className="paper-lab-card" aria-labelledby="paper-orders-title">
        <div className="paper-lab-card-heading">
          <h3 id="paper-orders-title">3. Retained order lifecycle and fills</h3>
          <button disabled={busy || !inspection} onClick={() => void refresh()} type="button">Refresh</button>
        </div>
        {!inspection ? <p>Retain a run before inspecting paper evidence.</p> : inspection.orders.length === 0 ? <p>No confirmed simulated orders yet.</p> : (
          <div className="paper-lab-order-list">
            {inspection.orders.map((row) => (
              <article className="paper-lab-order" data-selected={selectedOrderId === row.order.order_id} key={row.order.order_id}>
                <button className="paper-lab-order-select" onClick={() => setSelectedOrderId(row.order.order_id)} type="button">
                  <strong>{row.order.side.toUpperCase()} {row.order.quantity} · {row.order.instrument_id}</strong>
                  <span>{row.status} · remaining {row.remaining_quantity}</span>
                </button>
                <dl>
                  <div><dt>Order</dt><dd>{shortId(row.order.order_id)}</dd></div>
                  <div><dt>Assumptions</dt><dd>{shortId(row.order.assumption_id)}</dd></div>
                  <div><dt>Eligible</dt><dd>{row.order.eligible_at}</dd></div>
                  <div><dt>Fills</dt><dd>{row.fills.length}</dd></div>
                </dl>
                {row.lifecycle.length ? (
                  <ol className="paper-lab-timeline" aria-label={`Lifecycle for ${row.order.order_id}`}>
                    {row.lifecycle.map((event) => <li key={event.event_id}><strong>{event.status}</strong> · {event.reason}</li>)}
                  </ol>
                ) : null}
                {row.fills.map((fill) => (
                  <p className="paper-lab-fill" key={fill.fill_id}>
                    Fill #{fill.sequence}: {fill.quantity} @ {fill.execution_price}, fee {fill.fee} · bar {shortId(fill.bar_evidence_id)}
                  </p>
                ))}
                {!terminal(row.status) ? <button disabled={busy} onClick={() => void cancelOrder(row)} type="button">Cancel simulated order</button> : null}
              </article>
            ))}
          </div>
        )}
        {inspection ? (
          <div className="paper-lab-projection">
            <strong>D8 accounting revision {inspection.projection.revision}</strong>
            <span>Cash: {formatRecord(inspection.projection.cash_by_currency)}</span>
            <span>Projection: {inspection.projection.health}</span>
            <span>Equity: {inspection.projection.equity_base ?? "needs valuation evidence"}</span>
          </div>
        ) : null}
      </section>

      <form className="paper-lab-card" onSubmit={(event) => void processBar(event)}>
        <div className="paper-lab-card-heading">
          <h3>4. Governed completed-bar evidence</h3>
          <button disabled={busy} onClick={() => setBar(newBar())} type="button">New bar identity</button>
        </div>
        <p className="paper-lab-help">Paper Lab never fetches a provider or sends an order. Enter retained/local/synthetic governed bar evidence explicitly.</p>
        <div className="paper-lab-grid">
          <TextField label="Bar evidence UUID" value={bar.evidenceId} onChange={(value) => setBar({ ...bar, evidenceId: value })} />
          <TextField label="Instrument ID" value={bar.instrumentId} onChange={(value) => setBar({ ...bar, instrumentId: value })} />
          <TextField label="Dataset revision UUID" value={bar.datasetRevisionId} onChange={(value) => setBar({ ...bar, datasetRevisionId: value })} />
          <TextField label="Source ID" value={bar.marketSourceId} onChange={(value) => setBar({ ...bar, marketSourceId: value })} />
          <TextField label="Timeframe" value={bar.timeframe} onChange={(value) => setBar({ ...bar, timeframe: value })} />
          <TextField label="Bar start" value={bar.barStartedAt} onChange={(value) => setBar({ ...bar, barStartedAt: value })} />
          <TextField label="Bar end" value={bar.barEndedAt} onChange={(value) => setBar({ ...bar, barEndedAt: value })} />
          <TextField label="Available at" value={bar.availableAt} onChange={(value) => setBar({ ...bar, availableAt: value })} />
          <TextField label="Open" value={bar.open} onChange={(value) => setBar({ ...bar, open: value })} />
          <TextField label="High" value={bar.high} onChange={(value) => setBar({ ...bar, high: value })} />
          <TextField label="Low" value={bar.low} onChange={(value) => setBar({ ...bar, low: value })} />
          <TextField label="Close" value={bar.close} onChange={(value) => setBar({ ...bar, close: value })} />
          <TextField label="Volume" value={bar.volume ?? ""} onChange={(value) => setBar({ ...bar, volume: value })} required={false} />
          <TextField label="Market calendar" value={bar.marketCalendarId ?? ""} onChange={(value) => setBar({ ...bar, marketCalendarId: value })} required={false} />
          <label className="paper-lab-checkbox"><input checked={bar.complete} onChange={(event) => setBar({ ...bar, complete: event.target.checked })} type="checkbox" />Complete bar</label>
          <label className="paper-lab-checkbox"><input checked={bar.sessionOpen} onChange={(event) => setBar({ ...bar, sessionOpen: event.target.checked })} type="checkbox" />Market session open</label>
        </div>
        <div className="paper-lab-actions">
          <button disabled={busy || !selectedOrder} type="submit">Process bar for selected order</button>
          <button disabled={busy || !inspection} onClick={() => void appendMark()} type="button">Retain close as valuation mark</button>
          <button disabled={busy || !inspection} onClick={() => void checkpoint()} type="button">Checkpoint this bar</button>
        </div>
      </form>

      <form className="paper-lab-card" onSubmit={(event) => void compare(event)}>
        <div className="paper-lab-card-heading"><h3>5. Forward vs. backtest evidence</h3><span>Descriptive only</span></div>
        <div className="paper-lab-grid">
          <label>Backtest result ID<input min={1} type="number" value={backtestResultId} onChange={(event) => setBacktestResultId(Number(event.target.value))} /></label>
          <label>Strategy version ID<input min={1} type="number" value={strategyVersionId} onChange={(event) => setStrategyVersionId(Number(event.target.value))} /></label>
          <TextField label="Backtest start" value={backtestStart} onChange={setBacktestStart} />
          <TextField label="Backtest end" value={backtestEnd} onChange={setBacktestEnd} />
          <TextField label="Forward start" value={forwardStart} onChange={setForwardStart} />
          <TextField label="Forward end" value={forwardEnd} onChange={setForwardEnd} />
          <TextField label="Metric name" value={metricName} onChange={setMetricName} />
          <TextField label="Backtest value" value={backtestMetric} onChange={setBacktestMetric} />
          <TextField label="Forward value" value={forwardMetric} onChange={setForwardMetric} />
        </div>
        <button disabled={busy || !inspection} type="submit">Build descriptive comparison</button>
        {comparisonResult ? <pre className="paper-lab-comparison" aria-label="Descriptive comparison evidence">{JSON.stringify(comparisonResult.comparison, null, 2)}</pre> : null}
      </form>
    </section>
  );
}

function TextField({ label, value, onChange, required = true, disabled = false }: { label: string; value: string; onChange: (value: string) => void; required?: boolean; disabled?: boolean }) {
  return <label>{label}<input disabled={disabled} onChange={(event) => onChange(event.target.value)} required={required && !disabled} type="text" value={value} /></label>;
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return <label>{label}<input readOnly type="text" value={value} /></label>;
}

function parseLotAllocations(value: string): Record<string, string> {
  const result: Record<string, string> = {};
  for (const item of value.split(",")) {
    const [lotId, quantity] = item.split("=").map((part) => part.trim());
    if (!lotId || !quantity) throw new Error("Lot allocations must use lot-UUID=quantity pairs.");
    result[lotId] = quantity;
  }
  return result;
}

function errorMessage(error: unknown): string {
  if (error instanceof DesktopClientError) return error.message;
  return error instanceof Error ? error.message : "Paper Lab operation failed.";
}

function terminal(status: string): boolean {
  return ["filled", "cancelled", "expired", "rejected"].includes(status);
}

function shortId(value: string): string {
  return value.length <= 12 ? value : `${value.slice(0, 8)}…${value.slice(-4)}`;
}

function formatRecord(value: Record<string, string>): string {
  const entries = Object.entries(value);
  return entries.length ? entries.map(([key, amount]) => `${key} ${amount}`).join(" · ") : "none";
}
