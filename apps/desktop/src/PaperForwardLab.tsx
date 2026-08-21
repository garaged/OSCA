import { FormEvent, useEffect, useMemo, useState } from "react";
import { DesktopClientError } from "./api";
import {
  createPaperAccount,
  listPaperAccounts,
  PaperAccountRecord,
  recordPaperControl
} from "./paperAccountApi";
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
import { listPortfolios, VirtualPortfolio } from "./portfolioApi";
import "./paperForwardLab.css";

type Props = { profileRoot?: string };
type Feedback = { kind: "success" | "error"; message: string } | null;
type OrderType = "market" | "limit" | "stop" | "scheduled_market";

const nowIso = () => new Date().toISOString();

function newBar(
  instrumentId: string,
  datasetRevisionId: string,
  timeframe: string
): PaperBarInput {
  const started = new Date();
  const ended = new Date(started.getTime() + 60 * 60 * 1000);
  const available = new Date(ended.getTime() + 1000);
  return {
    evidenceId: crypto.randomUUID(),
    instrumentId,
    datasetRevisionId,
    marketSourceId: "local-paper-lab",
    timeframe,
    barStartedAt: started.toISOString(),
    barEndedAt: ended.toISOString(),
    availableAt: available.toISOString(),
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
  const [paperAccounts, setPaperAccounts] = useState<PaperAccountRecord[]>([]);
  const [paperAccountId, setPaperAccountId] = useState("");
  const [paperAccountName, setPaperAccountName] = useState("D9 paper research");
  const [paperRunId, setPaperRunId] = useState<string>(() => crypto.randomUUID());
  const [assumptionId, setAssumptionId] = useState<string>(() => crypto.randomUUID());
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

  const [draftId, setDraftId] = useState<string>(() => crypto.randomUUID());
  const [draftVersion, setDraftVersion] = useState(1);
  const [instrumentId, setInstrumentId] = useState("equity:XNAS:AAPL");
  const [timeframe, setTimeframe] = useState("1h");
  const [currency, setCurrency] = useState("USD");
  const [datasetRevisionId, setDatasetRevisionId] = useState<string>(() => crypto.randomUUID());
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<OrderType>("market");
  const [quantity, setQuantity] = useState("10");
  const [limitPrice, setLimitPrice] = useState("");
  const [stopPrice, setStopPrice] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [lotAllocationsText, setLotAllocationsText] = useState("");

  const [selectedOrderId, setSelectedOrderId] = useState("");
  const [bar, setBar] = useState<PaperBarInput>(() =>
    newBar("equity:XNAS:AAPL", datasetRevisionId, "1h")
  );

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
  const selectedPaperAccount = useMemo(
    () => paperAccounts.find((item) => item.account.paper_account_id === paperAccountId) ?? null,
    [paperAccounts, paperAccountId]
  );

  useEffect(() => {
    if (!profileRoot) {
      setPortfolios([]);
      setPortfolioId("");
      setPaperAccounts([]);
      setPaperAccountId("");
      return;
    }
    let active = true;
    void Promise.all([listPortfolios(profileRoot), listPaperAccounts(profileRoot)])
      .then(([portfolioResult, accountRecords]) => {
        if (!active) return;
        setPortfolios(portfolioResult.portfolios);
        setPortfolioId((current) => current || portfolioResult.portfolios[0]?.portfolio_id || "");
        setPaperAccounts(accountRecords);
        setPaperAccountId(
          (current) =>
            current ||
            accountRecords.find((item) => item.account.status === "active")?.account.paper_account_id ||
            ""
        );
      })
      .catch((error) => {
        if (active) setFeedback({ kind: "error", message: errorMessage(error) });
      });
    return () => {
      active = false;
    };
  }, [profileRoot]);

  async function reloadAccounts(preferredAccountId?: string) {
    if (!profileRoot) return;
    const records = await listPaperAccounts(profileRoot);
    setPaperAccounts(records);
    setPaperAccountId((current) => {
      const preferred = preferredAccountId ?? current;
      if (preferred && records.some((item) => item.account.paper_account_id === preferred)) {
        return preferred;
      }
      return records.find((item) => item.account.status === "active")?.account.paper_account_id ?? "";
    });
  }

  async function refresh() {
    if (!profileRoot || !paperRunId) return;
    const result = await inspectPaperRun(profileRoot, paperRunId);
    setInspection(result);
    if (!selectedOrderId && result.orders[0]) {
      setSelectedOrderId(result.orders[0].order.order_id);
    }
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

  async function createAccount() {
    if (!profileRoot || !paperAccountName.trim()) return;
    await perform(async () => {
      const selectedPortfolio = portfolios.find((item) => item.portfolio_id === portfolioId);
      const account = await createPaperAccount(
        profileRoot,
        paperAccountName.trim(),
        selectedPortfolio?.base_currency ?? "USD"
      );
      await reloadAccounts(account.paper_account_id);
    }, "Retained M8 paper account created for local simulated research.");
  }

  async function setControl(action: "allow" | "pause" | "kill_switch") {
    if (!profileRoot || !paperAccountId) return;
    await perform(async () => {
      await recordPaperControl(
        profileRoot,
        paperAccountId,
        action,
        `Paper Lab retained ${action} control decision`
      );
      await reloadAccounts(paperAccountId);
      if (inspection) await refresh();
    }, `Retained paper-account control: ${action}.`);
  }

  async function setupRun(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !portfolioId || !paperAccountId) return;
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
    if (!profileRoot || !portfolioId || !paperAccountId) return;
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
        ...(lotAllocationsText
          ? { lotAllocations: parseLotAllocations(lotAllocationsText) }
          : {})
      };
      await retainPaperDraft(profileRoot, input);
      setBar((current) => ({
        ...current,
        evidenceId: crypto.randomUUID(),
        instrumentId,
        datasetRevisionId,
        timeframe
      }));
      await refresh();
    }, `Draft v${draftVersion} retained. It is not active until explicitly confirmed.`);
  }

  async function confirmDraft() {
    if (!profileRoot) return;
    await perform(async () => {
      const result = await confirmPaperDraft(profileRoot, paperRunId, draftId, draftVersion);
      setSelectedOrderId(result.order.order_id);
      await reloadAccounts(paperAccountId);
      await refresh();
    }, "SIMULATED-ONLY order confirmed. No external destination exists.");
  }

  async function processBar(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !selectedOrderId || !paperAccountId) return;
    await perform(async () => {
      await processPaperBar(profileRoot, paperRunId, paperAccountId, selectedOrderId, bar);
      await reloadAccounts(paperAccountId);
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

  function startNewRun() {
    const nextDatasetRevision = crypto.randomUUID();
    setPaperRunId(crypto.randomUUID());
    setAssumptionId(crypto.randomUUID());
    setDraftId(crypto.randomUUID());
    setDraftVersion(1);
    setDatasetRevisionId(nextDatasetRevision);
    setBar(newBar(instrumentId, nextDatasetRevision, timeframe));
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
        <span>
          Confirmation activates research simulation only. It cannot submit an external order.
        </span>
      </aside>

      {feedback ? (
        <p
          className={`paper-lab-feedback ${feedback.kind}`}
          role={feedback.kind === "error" ? "alert" : "status"}
        >
          {feedback.message}
        </p>
      ) : null}

      <form className="paper-lab-card" onSubmit={(event) => void setupRun(event)}>
        <CardHeading title="1. Run, retained account and execution assumptions" note="Immutable evidence" />
        <div className="paper-lab-grid">
          <label>
            Virtual portfolio
            <select
              required
              value={portfolioId}
              onChange={(event) => setPortfolioId(event.target.value)}
            >
              <option value="">Select portfolio</option>
              {portfolios.map((portfolio) => (
                <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>
                  {portfolio.name} · {portfolio.base_currency}
                </option>
              ))}
            </select>
          </label>
          <label>
            Retained M8 paper account
            <select
              required
              value={paperAccountId}
              onChange={(event) => setPaperAccountId(event.target.value)}
            >
              <option value="">Select retained paper account</option>
              {paperAccounts.map(({ account, latest_control }) => (
                <option
                  disabled={account.status !== "active"}
                  key={account.paper_account_id}
                  value={account.paper_account_id}
                >
                  {account.name} · {account.base_currency} · {account.status}
                  {latest_control ? ` · ${latest_control.action}` : ""}
                </option>
              ))}
            </select>
          </label>
          <TextField
            label="New paper account name"
            value={paperAccountName}
            onChange={setPaperAccountName}
          />
          <ReadOnlyField label="Paper run ID" value={paperRunId} />
          <ReadOnlyField label="Paper account ID" value={paperAccountId || "select or create an account"} />
          <ReadOnlyField label="Assumption ID" value={assumptionId} />
          <TextField label="Spread (bps)" value={spreadBps} onChange={setSpreadBps} />
          <TextField label="Slippage (bps)" value={slippageBps} onChange={setSlippageBps} />
          <TextField label="Fee (bps)" value={feeBps} onChange={setFeeBps} />
          <TextField label="Flat fee" value={flatFee} onChange={setFlatFee} />
          <label>
            Latency (ms)
            <input
              min={0}
              type="number"
              value={latencyMs}
              onChange={(event) => setLatencyMs(Number(event.target.value))}
            />
          </label>
          <TextField
            label="Max volume participation"
            value={maxVolumeParticipation}
            onChange={setMaxVolumeParticipation}
          />
          <TextField
            label="Max order notional (optional)"
            value={maxOrderNotional}
            onChange={setMaxOrderNotional}
            required={false}
          />
          <TextField
            label="Max position notional (optional)"
            value={maxPositionNotional}
            onChange={setMaxPositionNotional}
            required={false}
          />
        </div>
        <div className="paper-lab-actions">
          <button disabled={busy || !portfolioId || !paperAccountName.trim()} type="button" onClick={() => void createAccount()}>
            Create retained paper account
          </button>
          <button disabled={busy || !paperAccountId} type="button" onClick={() => void setControl("allow")}>
            Allow simulation
          </button>
          <button disabled={busy || !paperAccountId} type="button" onClick={() => void setControl("pause")}>
            Pause simulation
          </button>
          <button disabled={busy || !paperAccountId} type="button" onClick={() => void setControl("kill_switch")}>
            Engage simulated kill switch
          </button>
        </div>
        <p className="paper-lab-help">
          Current retained control: {selectedPaperAccount?.latest_control?.action ?? "none yet"}.
          Account/control evidence is stored separately from D8 balances and cannot authorize live execution.
        </p>
        <button disabled={busy || !portfolioId || !paperAccountId} type="submit">
          Retain run + assumptions
        </button>
      </form>

      <form className="paper-lab-card" onSubmit={(event) => void saveDraft(event)}>
        <div className="paper-lab-card-heading">
          <h3>2. Immutable simulated-order draft</h3>
          <button
            disabled={busy}
            type="button"
            onClick={() => setDraftVersion((value) => value + 1)}
          >
            New draft version
          </button>
        </div>
        <div className="paper-lab-grid">
          <ReadOnlyField label="Draft ID" value={draftId} />
          <ReadOnlyField label="Version" value={String(draftVersion)} />
          <TextField label="Instrument ID" value={instrumentId} onChange={setInstrumentId} />
          <TextField label="Timeframe" value={timeframe} onChange={setTimeframe} />
          <TextField label="Currency" value={currency} onChange={setCurrency} />
          <TextField
            label="Dataset revision UUID"
            value={datasetRevisionId}
            onChange={setDatasetRevisionId}
          />
          <label>
            Side
            <select
              value={side}
              onChange={(event) => setSide(event.target.value as "buy" | "sell")}
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </label>
          <label>
            Simulated order type
            <select
              value={orderType}
              onChange={(event) => setOrderType(event.target.value as OrderType)}
            >
              <option value="market">Market</option>
              <option value="limit">Limit</option>
              <option value="stop">Stop</option>
              <option value="scheduled_market">Scheduled market</option>
            </select>
          </label>
          <TextField label="Quantity" value={quantity} onChange={setQuantity} />
          <TextField
            disabled={orderType !== "limit"}
            label="Limit price"
            required={false}
            value={limitPrice}
            onChange={setLimitPrice}
          />
          <TextField
            disabled={orderType !== "stop"}
            label="Stop price"
            required={false}
            value={stopPrice}
            onChange={setStopPrice}
          />
          <TextField
            disabled={orderType !== "scheduled_market"}
            label="Scheduled at (ISO-8601)"
            required={false}
            value={scheduledAt}
            onChange={setScheduledAt}
          />
          <TextField
            label="Expires at (optional ISO-8601)"
            required={false}
            value={expiresAt}
            onChange={setExpiresAt}
          />
          <TextField
            disabled={side !== "sell"}
            label="Sell lot allocations (lot UUID=quantity, comma separated)"
            required={false}
            value={lotAllocationsText}
            onChange={setLotAllocationsText}
          />
        </div>
        <div className="paper-lab-actions">
          <button disabled={busy || !inspection} type="submit">
            Retain draft v{draftVersion}
          </button>
          <button
            className="paper-lab-confirm"
            disabled={
              busy ||
              !inspection?.drafts.some(
                (item) => item.draft_id === draftId && item.draft_version === draftVersion
              )
            }
            type="button"
            onClick={() => void confirmDraft()}
          >
            Confirm SIMULATED-ONLY order
          </button>
        </div>
      </form>

      <section className="paper-lab-card" aria-labelledby="paper-orders-title">
        <div className="paper-lab-card-heading">
          <h3 id="paper-orders-title">3. Retained order lifecycle and fills</h3>
          <button disabled={busy || !inspection} type="button" onClick={() => void refresh()}>
            Refresh
          </button>
        </div>
        <OrderEvidence
          inspection={inspection}
          selectedOrderId={selectedOrderId}
          onSelect={setSelectedOrderId}
          onCancel={(row) => void cancelOrder(row)}
          busy={busy}
        />
      </section>

      <form className="paper-lab-card" onSubmit={(event) => void processBar(event)}>
        <div className="paper-lab-card-heading">
          <h3>4. Governed completed-bar evidence</h3>
          <button
            disabled={busy}
            type="button"
            onClick={() => setBar(newBar(instrumentId, datasetRevisionId, timeframe))}
          >
            New bar identity
          </button>
        </div>
        <p className="paper-lab-help">
          Paper Lab never fetches a provider or sends an order. Enter retained, local, or
          synthetic governed bar evidence explicitly. New bars inherit the draft instrument,
          timeframe, and dataset revision.
        </p>
        <div className="paper-lab-grid">
          <BarText label="Bar evidence UUID" field="evidenceId" bar={bar} setBar={setBar} />
          <BarText label="Instrument ID" field="instrumentId" bar={bar} setBar={setBar} />
          <BarText
            label="Dataset revision UUID"
            field="datasetRevisionId"
            bar={bar}
            setBar={setBar}
          />
          <BarText label="Source ID" field="marketSourceId" bar={bar} setBar={setBar} />
          <BarText label="Timeframe" field="timeframe" bar={bar} setBar={setBar} />
          <BarText label="Bar start" field="barStartedAt" bar={bar} setBar={setBar} />
          <BarText label="Bar end" field="barEndedAt" bar={bar} setBar={setBar} />
          <BarText label="Available at" field="availableAt" bar={bar} setBar={setBar} />
          <BarText label="Open" field="open" bar={bar} setBar={setBar} />
          <BarText label="High" field="high" bar={bar} setBar={setBar} />
          <BarText label="Low" field="low" bar={bar} setBar={setBar} />
          <BarText label="Close" field="close" bar={bar} setBar={setBar} />
          <BarText label="Volume" field="volume" bar={bar} setBar={setBar} required={false} />
          <BarText
            label="Market calendar"
            field="marketCalendarId"
            bar={bar}
            setBar={setBar}
            required={false}
          />
          <label className="paper-lab-checkbox">
            <input
              checked={bar.complete}
              type="checkbox"
              onChange={(event) => setBar({ ...bar, complete: event.target.checked })}
            />
            Complete bar
          </label>
          <label className="paper-lab-checkbox">
            <input
              checked={bar.sessionOpen}
              type="checkbox"
              onChange={(event) => setBar({ ...bar, sessionOpen: event.target.checked })}
            />
            Market session open
          </label>
        </div>
        <div className="paper-lab-actions">
          <button disabled={busy || !selectedOrder} type="submit">
            Process bar for selected order
          </button>
          <button disabled={busy || !inspection} type="button" onClick={() => void appendMark()}>
            Retain close as valuation mark
          </button>
          <button disabled={busy || !inspection} type="button" onClick={() => void checkpoint()}>
            Checkpoint this bar
          </button>
        </div>
      </form>

      <form className="paper-lab-card" onSubmit={(event) => void compare(event)}>
        <CardHeading title="5. Forward vs. backtest evidence" note="Descriptive only" />
        <div className="paper-lab-grid">
          <label>
            Backtest result ID
            <input
              min={1}
              type="number"
              value={backtestResultId}
              onChange={(event) => setBacktestResultId(Number(event.target.value))}
            />
          </label>
          <label>
            Strategy version ID
            <input
              min={1}
              type="number"
              value={strategyVersionId}
              onChange={(event) => setStrategyVersionId(Number(event.target.value))}
            />
          </label>
          <TextField label="Backtest start" value={backtestStart} onChange={setBacktestStart} />
          <TextField label="Backtest end" value={backtestEnd} onChange={setBacktestEnd} />
          <TextField label="Forward start" value={forwardStart} onChange={setForwardStart} />
          <TextField label="Forward end" value={forwardEnd} onChange={setForwardEnd} />
          <TextField label="Metric name" value={metricName} onChange={setMetricName} />
          <TextField label="Backtest value" value={backtestMetric} onChange={setBacktestMetric} />
          <TextField label="Forward value" value={forwardMetric} onChange={setForwardMetric} />
        </div>
        <button disabled={busy || !inspection} type="submit">
          Build descriptive comparison
        </button>
        {comparisonResult ? (
          <pre className="paper-lab-comparison" aria-label="Descriptive comparison evidence">
            {JSON.stringify(comparisonResult.comparison, null, 2)}
          </pre>
        ) : null}
      </form>
    </section>
  );
}

function CardHeading({ title, note }: { title: string; note: string }) {
  return (
    <div className="paper-lab-card-heading">
      <h3>{title}</h3>
      <span>{note}</span>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange,
  required = true,
  disabled = false
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
}) {
  return (
    <label>
      {label}
      <input
        disabled={disabled}
        required={required && !disabled}
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <label>
      {label}
      <input readOnly type="text" value={value} />
    </label>
  );
}

function BarText({
  label,
  field,
  bar,
  setBar,
  required = true
}: {
  label: string;
  field: keyof Pick<
    PaperBarInput,
    | "evidenceId"
    | "instrumentId"
    | "datasetRevisionId"
    | "marketSourceId"
    | "timeframe"
    | "barStartedAt"
    | "barEndedAt"
    | "availableAt"
    | "open"
    | "high"
    | "low"
    | "close"
    | "volume"
    | "marketCalendarId"
  >;
  bar: PaperBarInput;
  setBar: (value: PaperBarInput) => void;
  required?: boolean;
}) {
  return (
    <TextField
      label={label}
      required={required}
      value={bar[field] ?? ""}
      onChange={(value) => setBar({ ...bar, [field]: value })}
    />
  );
}

function OrderEvidence({
  inspection,
  selectedOrderId,
  onSelect,
  onCancel,
  busy
}: {
  inspection: PaperRunInspection | null;
  selectedOrderId: string;
  onSelect: (value: string) => void;
  onCancel: (row: PaperOrderRow) => void;
  busy: boolean;
}) {
  if (!inspection) return <p>Retain a run before inspecting paper evidence.</p>;
  return (
    <>
      {inspection.orders.length === 0 ? (
        <p>No confirmed simulated orders yet.</p>
      ) : (
        <div className="paper-lab-order-list">
          {inspection.orders.map((row) => (
            <article
              className="paper-lab-order"
              data-selected={selectedOrderId === row.order.order_id}
              key={row.order.order_id}
            >
              <button
                className="paper-lab-order-select"
                type="button"
                onClick={() => onSelect(row.order.order_id)}
              >
                <strong>
                  {row.order.side.toUpperCase()} {row.order.quantity} · {row.order.instrument_id}
                </strong>
                <span>
                  {row.status} · remaining {row.remaining_quantity}
                </span>
              </button>
              <dl>
                <div><dt>Order</dt><dd>{shortId(row.order.order_id)}</dd></div>
                <div><dt>Assumptions</dt><dd>{shortId(row.order.assumption_id)}</dd></div>
                <div><dt>Eligible</dt><dd>{row.order.eligible_at}</dd></div>
                <div><dt>Fills</dt><dd>{row.fills.length}</dd></div>
              </dl>
              {row.lifecycle.length ? (
                <ol className="paper-lab-timeline" aria-label={`Lifecycle for ${row.order.order_id}`}>
                  {row.lifecycle.map((event) => (
                    <li key={event.event_id}><strong>{event.status}</strong> · {event.reason}</li>
                  ))}
                </ol>
              ) : null}
              {row.fills.map((fill) => (
                <p className="paper-lab-fill" key={fill.fill_id}>
                  Fill #{fill.sequence}: {fill.quantity} @ {fill.execution_price}, fee {fill.fee} · bar {shortId(fill.bar_evidence_id)}
                </p>
              ))}
              {!terminal(row.status) ? (
                <button disabled={busy} type="button" onClick={() => onCancel(row)}>
                  Cancel simulated order
                </button>
              ) : null}
            </article>
          ))}
        </div>
      )}
      <div className="paper-lab-projection">
        <strong>D8 accounting revision {inspection.projection.revision}</strong>
        <span>Cash: {formatRecord(inspection.projection.cash_by_currency)}</span>
        <span>Projection: {inspection.projection.health}</span>
        <span>Equity: {inspection.projection.equity_base ?? "needs valuation evidence"}</span>
      </div>
    </>
  );
}

function parseLotAllocations(value: string): Record<string, string> {
  const result: Record<string, string> = {};
  for (const item of value.split(",")) {
    const [lotId, allocatedQuantity] = item.split("=").map((part) => part.trim());
    if (!lotId || !allocatedQuantity) {
      throw new Error("Lot allocations must use lot-UUID=quantity pairs.");
    }
    result[lotId] = allocatedQuantity;
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
  return entries.length
    ? entries.map(([key, amount]) => `${key} ${amount}`).join(" · ")
    : "none";
}
