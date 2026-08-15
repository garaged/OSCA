import { FormEvent, useEffect, useState } from "react";
import {
  createPortfolio,
  getPortfolio,
  listPortfolios,
  PortfolioDetail,
  recordAcquisition,
  recordValuation,
  VirtualPortfolio
} from "./portfolioApi";
import "./portfolioLab.css";

type LoadState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready" }
  | { kind: "error"; message: string };

export function PortfolioLabSurface({ profileRoot }: { profileRoot?: string }) {
  const [state, setState] = useState<LoadState>({ kind: "idle" });
  const [portfolios, setPortfolios] = useState<VirtualPortfolio[]>([]);
  const [active, setActive] = useState<PortfolioDetail | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [name, setName] = useState("Research portfolio");
  const [startingCash, setStartingCash] = useState("10000");
  const [instrument, setInstrument] = useState("equity:XNAS:AAPL");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("100");
  const [fee, setFee] = useState("0");
  const [valuationPrice, setValuationPrice] = useState("100");

  async function reload(selectId?: string) {
    if (!profileRoot) {
      setPortfolios([]);
      setActive(null);
      setState({ kind: "ready" });
      return;
    }
    setState({ kind: "loading" });
    try {
      const listed = await listPortfolios(profileRoot);
      setPortfolios(listed.portfolios);
      const selected =
        listed.portfolios.find((portfolio) => portfolio.portfolio_id === selectId) ??
        listed.portfolios[0];
      setActive(selected ? await getPortfolio(profileRoot, selected.portfolio_id) : null);
      setState({ kind: "ready" });
    } catch (error) {
      setState({ kind: "error", message: message(error) });
    }
  }

  useEffect(() => {
    void reload();
  }, [profileRoot]);

  async function selectPortfolio(portfolioId: string) {
    if (!profileRoot) return;
    setState({ kind: "loading" });
    try {
      setActive(await getPortfolio(profileRoot, portfolioId));
      setState({ kind: "ready" });
    } catch (error) {
      setState({ kind: "error", message: message(error) });
    }
  }

  async function submitPortfolio(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    try {
      const created = await createPortfolio(profileRoot, name, "USD", startingCash);
      setNotice("Virtual portfolio created with immutable starting-cash evidence.");
      await reload(created.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitAcquisition(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !active) return;
    try {
      const updated = await recordAcquisition(
        profileRoot,
        active.portfolio.portfolio_id,
        instrument,
        quantity,
        unitPrice,
        active.portfolio.base_currency,
        fee,
        crypto.randomUUID()
      );
      setNotice("Simulated acquisition journaled. No order was sent anywhere.");
      setActive(await getPortfolio(profileRoot, updated.portfolio.portfolio_id));
      await reload(updated.portfolio.portfolio_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitValuation(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || !active) return;
    const position = active.projection.positions.find(
      (item) => item.instrument_id === instrument
    );
    if (!position) {
      setNotice("Add or select a held instrument before recording valuation evidence.");
      return;
    }
    try {
      const updated = await recordValuation(
        profileRoot,
        active.portfolio.portfolio_id,
        instrument,
        position.quantity,
        valuationPrice,
        position.currency,
        "manual-local-evidence",
        new Date().toISOString(),
        crypto.randomUUID()
      );
      setNotice("Local valuation evidence retained with source and effective time.");
      setActive(await getPortfolio(profileRoot, updated.portfolio.portfolio_id));
    } catch (error) {
      setNotice(message(error));
    }
  }

  return (
    <section className="portfolio-lab" aria-labelledby="portfolio-lab-heading">
      <header className="portfolio-lab-hero">
        <div>
          <p className="eyebrow">D8 simulated accounting</p>
          <h1 id="portfolio-lab-heading">Portfolio Lab</h1>
          <p>
            Inspect journal-backed virtual portfolios, explicit lots, and valuation evidence.
            This is research accounting only, not brokerage or investment advice.
          </p>
        </div>
        <div className="portfolio-lab-boundaries" aria-label="Portfolio Lab boundaries">
          <span>Append-only journal</span>
          <span>Local evidence</span>
          <span>No real capital</span>
        </div>
      </header>

      {notice ? <p className="portfolio-lab-notice" role="status">{notice}</p> : null}
      {!profileRoot ? (
        <p className="portfolio-lab-notice" role="note">
          Open a validated profile from Workspace before using Portfolio Lab.
        </p>
      ) : null}
      {state.kind === "loading" ? <p role="status">Loading portfolio evidence…</p> : null}
      {state.kind === "error" ? <p role="alert">{state.message}</p> : null}

      <div className="portfolio-lab-layout">
        <section className="portfolio-lab-panel" aria-labelledby="portfolio-create-title">
          <h2 id="portfolio-create-title">Create virtual portfolio</h2>
          <form className="portfolio-lab-form" onSubmit={(event) => void submitPortfolio(event)}>
            <label>
              Name
              <input value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <label>
              Starting cash (USD)
              <input
                inputMode="decimal"
                value={startingCash}
                onChange={(event) => setStartingCash(event.target.value)}
              />
            </label>
            <button disabled={!profileRoot} type="submit">Create portfolio</button>
          </form>
        </section>

        <section className="portfolio-lab-panel" aria-labelledby="portfolio-list-title">
          <h2 id="portfolio-list-title">Virtual portfolios</h2>
          {portfolios.length === 0 ? <p>No virtual portfolios yet.</p> : null}
          <div className="portfolio-list">
            {portfolios.map((portfolio) => (
              <button
                aria-pressed={active?.portfolio.portfolio_id === portfolio.portfolio_id}
                key={portfolio.portfolio_id}
                onClick={() => void selectPortfolio(portfolio.portfolio_id)}
                type="button"
              >
                <strong>{portfolio.name}</strong>
                <span>{portfolio.base_currency} · {portfolio.status}</span>
              </button>
            ))}
          </div>
        </section>
      </div>

      {active ? (
        <>
          <section className="portfolio-lab-panel" aria-labelledby="portfolio-summary-title">
            <div className="portfolio-lab-heading-row">
              <div>
                <h2 id="portfolio-summary-title">{active.portfolio.name}</h2>
                <p>Revision {active.projection.revision} · {active.portfolio.base_currency} base currency</p>
              </div>
              <span className={`portfolio-health portfolio-health-${active.projection.health}`}>
                {active.projection.health}
              </span>
            </div>
            {active.projection.missing_evidence.length > 0 ? (
              <div className="portfolio-degraded" role="status">
                <strong>Valuation evidence incomplete.</strong>
                <ul>
                  {active.projection.missing_evidence.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            ) : null}
            <dl className="portfolio-metrics">
              <div><dt>Cash</dt><dd>{formatRecord(active.projection.cash_by_currency)}</dd></div>
              <div><dt>Equity</dt><dd>{value(active.projection.equity_base, active.portfolio.base_currency)}</dd></div>
              <div><dt>Unrealized P&amp;L</dt><dd>{value(active.projection.unrealized_pnl_base, active.portfolio.base_currency)}</dd></div>
              <div><dt>Gross exposure</dt><dd>{value(active.projection.gross_exposure_base, active.portfolio.base_currency)}</dd></div>
              <div><dt>Realized P&amp;L</dt><dd>{formatRecord(active.projection.realized_pnl_by_currency)}</dd></div>
              <div><dt>Fees</dt><dd>{formatRecord(active.projection.fees_by_currency)}</dd></div>
            </dl>
          </section>

          <div className="portfolio-lab-layout">
            <section className="portfolio-lab-panel" aria-labelledby="portfolio-acquisition-title">
              <h2 id="portfolio-acquisition-title">Record simulated acquisition</h2>
              <form className="portfolio-lab-form" onSubmit={(event) => void submitAcquisition(event)}>
                <label>Instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
                <label>Quantity<input inputMode="decimal" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label>
                <label>Unit price<input inputMode="decimal" value={unitPrice} onChange={(event) => setUnitPrice(event.target.value)} /></label>
                <label>Fee<input inputMode="decimal" value={fee} onChange={(event) => setFee(event.target.value)} /></label>
                <button type="submit">Journal acquisition</button>
              </form>
            </section>

            <section className="portfolio-lab-panel" aria-labelledby="portfolio-valuation-title">
              <h2 id="portfolio-valuation-title">Record local valuation</h2>
              <form className="portfolio-lab-form" onSubmit={(event) => void submitValuation(event)}>
                <label>Instrument<input value={instrument} onChange={(event) => setInstrument(event.target.value)} /></label>
                <label>Unit price<input inputMode="decimal" value={valuationPrice} onChange={(event) => setValuationPrice(event.target.value)} /></label>
                <button disabled={active.projection.positions.length === 0} type="submit">Retain valuation evidence</button>
              </form>
              <p className="portfolio-lab-hint">Manual local evidence is explicitly sourced and timestamped.</p>
            </section>
          </div>

          <section className="portfolio-lab-panel" aria-labelledby="portfolio-position-title">
            <h2 id="portfolio-position-title">Positions and lots</h2>
            <div className="portfolio-table-wrap">
              <table>
                <caption className="visually-hidden">Virtual portfolio positions</caption>
                <thead><tr><th>Instrument</th><th>Quantity</th><th>Book cost</th><th>Currency</th></tr></thead>
                <tbody>
                  {active.projection.positions.map((position) => (
                    <tr key={`${position.instrument_id}-${position.currency}`}>
                      <td>{position.instrument_id}</td><td>{position.quantity}</td><td>{position.book_cost}</td><td>{position.currency}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <details>
              <summary>Open lot evidence ({active.projection.lots.length})</summary>
              <ul className="portfolio-evidence-list">
                {active.projection.lots.map((lot) => (
                  <li key={lot.lot_id}>
                    <strong>{lot.instrument_id}</strong> · {lot.quantity} · {lot.book_cost} {lot.currency}
                    <small>{lot.lot_id}</small>
                  </li>
                ))}
              </ul>
            </details>
          </section>

          <section className="portfolio-lab-panel" aria-labelledby="portfolio-journal-title">
            <h2 id="portfolio-journal-title">Immutable journal evidence</h2>
            <p>{active.events.length} economic event(s) · {active.journal.length} balanced transaction(s)</p>
            <ol className="portfolio-evidence-list">
              {active.journal.map((transaction) => (
                <li key={transaction.transaction_id}>
                  <strong>{transaction.effective_at}</strong>
                  <ul>
                    {transaction.postings.map((posting) => (
                      <li key={posting.posting_id}>
                        {posting.side} {posting.amount} {posting.currency} · {posting.account_code}
                        {posting.instrument_id ? ` · ${posting.instrument_id}` : ""}
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>
          </section>

          <section className="portfolio-lab-panel" aria-labelledby="portfolio-provenance-title">
            <h2 id="portfolio-provenance-title">Valuation provenance</h2>
            {active.valuations.length === 0 ? <p>No valuation observations retained yet.</p> : (
              <ul className="portfolio-evidence-list">
                {active.valuations.map((observation) => (
                  <li key={observation.observation_id}>
                    <strong>{observation.asset_id}</strong> · {observation.unit_price} {observation.price_currency}
                    <span>{observation.price_source} · {observation.price_effective_at} · revision {observation.valuation_revision}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      ) : null}
    </section>
  );
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : "Portfolio Lab operation failed.";
}

function formatRecord(record: Record<string, string>): string {
  const entries = Object.entries(record);
  return entries.length === 0
    ? "—"
    : entries.map(([currency, amount]) => `${amount} ${currency}`).join(" · ");
}

function value(amount: string | null, currency: string): string {
  return amount == null ? "Unavailable" : `${amount} ${currency}`;
}
