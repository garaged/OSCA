import { FormEvent, useEffect, useState } from "react";
import { getPortfolio, listPortfolios, PortfolioDetail, VirtualPortfolio } from "./portfolioApi";
import {
  clonePortfolio,
  preparePortfolioExport,
  recordDisposal,
  recordDividend,
  recordFork,
  recordFxConversion,
  recordSplit,
  resetPortfolio,
  restorePortfolio,
  reverseAccountingEvent
} from "./portfolioOperationsApi";

export function PortfolioOperationsSurface({ profileRoot }: { profileRoot?: string }) {
  const [portfolios, setPortfolios] = useState<VirtualPortfolio[]>([]);
  const [portfolioId, setPortfolioId] = useState("");
  const [detail, setDetail] = useState<PortfolioDetail | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [instrument, setInstrument] = useState("AAPL");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("100");
  const [fee, setFee] = useState("0");
  const [lotId, setLotId] = useState("");
  const [dividendAmount, setDividendAmount] = useState("10");
  const [splitFactor, setSplitFactor] = useState("2");
  const [forkInstrument, setForkInstrument] = useState("NEW");
  const [forkQuantity, setForkQuantity] = useState("1");
  const [forkBookCost, setForkBookCost] = useState("0");
  const [fromCurrency, setFromCurrency] = useState("USD");
  const [fromAmount, setFromAmount] = useState("100");
  const [toCurrency, setToCurrency] = useState("EUR");
  const [toAmount, setToAmount] = useState("90");
  const [eventId, setEventId] = useState("");
  const [reversalReason, setReversalReason] = useState("Manual correction");
  const [cloneName, setCloneName] = useState("Portfolio clone");
  const [resetName, setResetName] = useState("Reset successor");
  const [resetCash, setResetCash] = useState("10000");
  const [restorePath, setRestorePath] = useState("");
  const [exportPath, setExportPath] = useState<string | null>(null);

  async function reload(targetId?: string) {
    if (!profileRoot) {
      setPortfolios([]);
      setPortfolioId("");
      setDetail(null);
      return;
    }
    try {
      const listed = await listPortfolios(profileRoot);
      setPortfolios(listed.portfolios);
      const selected =
        listed.portfolios.find((item) => item.portfolio_id === targetId) ??
        listed.portfolios.find((item) => item.portfolio_id === portfolioId) ??
        listed.portfolios[0];
      if (!selected) {
        setPortfolioId("");
        setDetail(null);
        return;
      }
      setPortfolioId(selected.portfolio_id);
      const loaded = await getPortfolio(profileRoot, selected.portfolio_id);
      setDetail(loaded);
      const firstPosition = loaded.projection.positions[0];
      if (firstPosition) {
        setInstrument(firstPosition.instrument_id);
      }
      const firstLot = loaded.projection.lots[0];
      setLotId(firstLot?.lot_id ?? "");
      const reversible = loaded.events.find(
        (event) => event.sequence > 1 && event.event_type !== "reversal"
      );
      setEventId(reversible?.event_id ?? "");
    } catch (error) {
      setNotice(message(error));
    }
  }

  useEffect(() => {
    void reload();
  }, [profileRoot]);

  async function selectPortfolio(targetId: string) {
    await reload(targetId);
  }

  async function submitDisposal(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail) return;
    try {
      await recordDisposal(profileRoot, detail.portfolio.portfolio_id, {
        instrumentId: instrument,
        quantity,
        unitPrice,
        currency: detail.portfolio.base_currency,
        fee,
        sourceId: crypto.randomUUID(),
        ...(lotId ? { lotAllocations: { [lotId]: quantity } } : {})
      });
      setNotice("Simulated disposal journaled. No market order was sent.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitDividend(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail) return;
    try {
      await recordDividend(
        profileRoot,
        detail.portfolio.portfolio_id,
        instrument,
        dividendAmount,
        detail.portfolio.base_currency,
        crypto.randomUUID()
      );
      setNotice("Dividend/distribution retained as journal evidence.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitSplit(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail) return;
    try {
      await recordSplit(
        profileRoot,
        detail.portfolio.portfolio_id,
        instrument,
        splitFactor,
        crypto.randomUUID()
      );
      setNotice("Split applied once through immutable corporate-action evidence.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitFork(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail) return;
    try {
      await recordFork(profileRoot, detail.portfolio.portfolio_id, {
        sourceInstrumentId: instrument,
        newInstrumentId: forkInstrument,
        newQuantity: forkQuantity,
        currency: detail.portfolio.base_currency,
        allocatedBookCost: forkBookCost,
        sourceId: crypto.randomUUID(),
        ...(lotId && forkBookCost !== "0"
          ? { sourceLotAllocations: { [lotId]: forkBookCost } }
          : {})
      });
      setNotice("Fork/distribution retained with explicit source-lot book-cost evidence.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitFx(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail) return;
    try {
      await recordFxConversion(
        profileRoot,
        detail.portfolio.portfolio_id,
        fromCurrency,
        fromAmount,
        toCurrency,
        toAmount,
        crypto.randomUUID()
      );
      setNotice("FX cash conversion retained as balanced multi-currency evidence.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitReversal(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !detail || !eventId) return;
    try {
      await reverseAccountingEvent(
        profileRoot,
        detail.portfolio.portfolio_id,
        eventId,
        reversalReason,
        crypto.randomUUID()
      );
      setNotice("Correction appended as a compensating reversal; original evidence was preserved.");
      await reload(detail.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function doClone() {
    if (!profileRoot || !detail) return;
    try {
      const createdId = await clonePortfolio(
        profileRoot,
        detail.portfolio.portfolio_id,
        cloneName
      );
      setNotice("Independent clone created with source revision lineage.");
      await reload(createdId);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function doReset() {
    if (!profileRoot || !detail) return;
    try {
      const createdId = await resetPortfolio(
        profileRoot,
        detail.portfolio.portfolio_id,
        resetName,
        resetCash
      );
      setNotice("Reset created a fresh successor; source journal remains unchanged.");
      await reload(createdId);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function doExport() {
    if (!profileRoot || !detail) return;
    try {
      const result = await preparePortfolioExport(
        profileRoot,
        detail.portfolio.portfolio_id
      );
      setExportPath(result.output_path);
      setRestorePath(result.output_path);
      setNotice("Portable digest-protected portfolio bundle prepared without provider payloads.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function doRestore() {
    if (!profileRoot || !restorePath.trim()) return;
    try {
      const restoredId = await restorePortfolio(profileRoot, restorePath.trim());
      setNotice("Portfolio bundle validated and restored atomically.");
      await reload(restoredId);
    } catch (error) {
      setNotice(message(error));
    }
  }

  return (
    <section className="portfolio-lab-panel portfolio-operations" aria-labelledby="portfolio-operations-title">
      <div className="portfolio-lab-heading-row">
        <div>
          <p className="eyebrow">Journal-backed operations</p>
          <h2 id="portfolio-operations-title">Accounting operations and lifecycle</h2>
          <p>
            These controls append simulated research evidence only. They do not connect to a broker,
            submit an order, or move real capital.
          </p>
        </div>
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

      {detail ? (
        <div className="portfolio-operations-grid">
          <details open>
            <summary>Simulated disposal</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitDisposal(event)}>
              <label>Instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
              <label>Quantity<input inputMode="decimal" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label>
              <label>Unit price<input inputMode="decimal" value={unitPrice} onChange={(event) => setUnitPrice(event.target.value)} /></label>
              <label>Fee<input inputMode="decimal" value={fee} onChange={(event) => setFee(event.target.value)} /></label>
              <label>
                Lot allocation
                <select value={lotId} onChange={(event) => setLotId(event.target.value)}>
                  <option value="">No explicit lot</option>
                  {detail.projection.lots.filter((lot) => lot.instrument_id === instrument).map((lot) => (
                    <option key={lot.lot_id} value={lot.lot_id}>{lot.lot_id} · {lot.quantity}</option>
                  ))}
                </select>
              </label>
              <button disabled={detail.projection.positions.length === 0} type="submit">Journal disposal</button>
            </form>
          </details>

          <details>
            <summary>Dividend / distribution</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitDividend(event)}>
              <label>Instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
              <label>Cash amount<input inputMode="decimal" value={dividendAmount} onChange={(event) => setDividendAmount(event.target.value)} /></label>
              <button type="submit">Journal distribution</button>
            </form>
          </details>

          <details>
            <summary>Split</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitSplit(event)}>
              <label>Instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
              <label>Factor<input inputMode="decimal" value={splitFactor} onChange={(event) => setSplitFactor(event.target.value)} /></label>
              <button disabled={detail.projection.positions.length === 0} type="submit">Apply split evidence</button>
            </form>
          </details>

          <details>
            <summary>Crypto fork / asset distribution</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitFork(event)}>
              <label>Source instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
              <label>New instrument<input value={forkInstrument} onChange={(event) => setForkInstrument(event.target.value)} /></label>
              <label>New quantity<input inputMode="decimal" value={forkQuantity} onChange={(event) => setForkQuantity(event.target.value)} /></label>
              <label>Allocated book cost<input inputMode="decimal" value={forkBookCost} onChange={(event) => setForkBookCost(event.target.value)} /></label>
              <button disabled={detail.projection.positions.length === 0} type="submit">Journal fork evidence</button>
            </form>
          </details>

          <details>
            <summary>FX cash conversion</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitFx(event)}>
              <label>From currency<input maxLength={3} value={fromCurrency} onChange={(event) => setFromCurrency(event.target.value.toUpperCase())} /></label>
              <label>From amount<input inputMode="decimal" value={fromAmount} onChange={(event) => setFromAmount(event.target.value)} /></label>
              <label>To currency<input maxLength={3} value={toCurrency} onChange={(event) => setToCurrency(event.target.value.toUpperCase())} /></label>
              <label>To amount<input inputMode="decimal" value={toAmount} onChange={(event) => setToAmount(event.target.value)} /></label>
              <button type="submit">Journal FX conversion</button>
            </form>
          </details>

          <details>
            <summary>Correction reversal</summary>
            <form className="portfolio-lab-form" onSubmit={(event) => void submitReversal(event)}>
              <label>
                Original event
                <select value={eventId} onChange={(event) => setEventId(event.target.value)}>
                  <option value="">Select event</option>
                  {detail.events.filter((item) => item.sequence > 1 && item.event_type !== "reversal").map((item) => (
                    <option key={item.event_id} value={item.event_id}>#{item.sequence} · {item.event_type} · {item.source_id}</option>
                  ))}
                </select>
              </label>
              <label>Reason<input value={reversalReason} onChange={(event) => setReversalReason(event.target.value)} /></label>
              <button disabled={!eventId} type="submit">Append reversal</button>
            </form>
          </details>

          <details>
            <summary>Clone / reset</summary>
            <div className="portfolio-lab-form">
              <label>Clone name<input value={cloneName} onChange={(event) => setCloneName(event.target.value)} /></label>
              <button onClick={() => void doClone()} type="button">Clone current revision</button>
              <label>Reset successor name<input value={resetName} onChange={(event) => setResetName(event.target.value)} /></label>
              <label>Reset starting cash<input inputMode="decimal" value={resetCash} onChange={(event) => setResetCash(event.target.value)} /></label>
              <button onClick={() => void doReset()} type="button">Create reset successor</button>
            </div>
          </details>

          <details>
            <summary>Portable export / restore</summary>
            <div className="portfolio-lab-form">
              <button onClick={() => void doExport()} type="button">Prepare portable bundle</button>
              {exportPath ? <p className="portfolio-path">{exportPath}</p> : null}
              <label>Bundle path<input value={restorePath} onChange={(event) => setRestorePath(event.target.value)} /></label>
              <button disabled={!restorePath.trim()} onClick={() => void doRestore()} type="button">Validate and restore bundle</button>
            </div>
          </details>
        </div>
      ) : <p>No virtual portfolio selected.</p>}
    </section>
  );
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : "Portfolio accounting operation failed.";
}
