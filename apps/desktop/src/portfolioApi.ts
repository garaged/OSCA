import { invoke } from "@tauri-apps/api/core";
import { DesktopClientError, DesktopErrorPayload } from "./api";

export type VirtualPortfolio = {
  portfolio_id: string;
  name: string;
  base_currency: string;
  status: "active" | "closed";
  created_at: string;
  source_portfolio_id: string | null;
  source_revision: number | null;
  lineage_kind: string | null;
};

export type PortfolioPosition = {
  instrument_id: string;
  quantity: string;
  book_cost: string;
  currency: string;
};

export type PortfolioLot = PortfolioPosition & {
  lot_id: string;
  acquired_at: string;
};

export type PortfolioProjection = {
  portfolio_id: string;
  revision: number;
  base_currency: string;
  cash_by_currency: Record<string, string>;
  positions: PortfolioPosition[];
  lots: PortfolioLot[];
  realized_pnl_by_currency: Record<string, string>;
  income_by_currency: Record<string, string>;
  fees_by_currency: Record<string, string>;
  health: "healthy" | "degraded";
  missing_evidence: string[];
  equity_base: string | null;
  unrealized_pnl_base: string | null;
  gross_exposure_base: string | null;
  net_exposure_base: string | null;
  allocation_by_asset: Record<string, string>;
};

export type JournalPosting = {
  posting_id: string;
  account_code: string;
  side: "debit" | "credit";
  currency: string;
  amount: string;
  instrument_id: string | null;
};

export type JournalTransaction = {
  transaction_id: string;
  event_id: string;
  effective_at: string;
  postings: JournalPosting[];
};

export type AccountingEvent = {
  event_id: string;
  sequence: number;
  event_type: string;
  effective_at: string;
  source_kind: string;
  source_id: string;
  content_digest: string;
};

export type ValuationObservation = {
  observation_id: string;
  asset_id: string;
  quantity: string;
  unit_price: string;
  price_currency: string;
  price_source: string;
  price_effective_at: string;
  fx_rate_to_base: string | null;
  fx_source: string | null;
  fx_effective_at: string | null;
  valuation_revision: string;
};

export type PortfolioDetail = {
  portfolio: VirtualPortfolio;
  projection: PortfolioProjection;
  events: AccountingEvent[];
  journal: JournalTransaction[];
  valuations: ValuationObservation[];
  network_access_enabled: false;
  recommendations_enabled: false;
  broker_connections_enabled: false;
  autonomous_execution_enabled: false;
  live_order_execution: false;
  real_capital_execution_enabled: false;
};

export type PortfolioList = {
  portfolios: VirtualPortfolio[];
  network_access_enabled: false;
  recommendations_enabled: false;
  real_capital_execution_enabled: false;
};

type Envelope = {
  protocol_version: string;
  request_id: string;
  status: "ok" | "error";
  result: Record<string, unknown> | null;
  error: DesktopErrorPayload | null;
};

export async function listPortfolios(profileRoot: string): Promise<PortfolioList> {
  return request("portfolio.list", { profile_root: profileRoot }, parsePortfolioList);
}

export async function getPortfolio(
  profileRoot: string,
  portfolioId: string
): Promise<PortfolioDetail> {
  return request(
    "portfolio.get",
    { profile_root: profileRoot, portfolio_id: portfolioId },
    parsePortfolioDetail
  );
}

export async function createPortfolio(
  profileRoot: string,
  name: string,
  baseCurrency: string,
  startingCash: string
): Promise<PortfolioDetail> {
  return request(
    "portfolio.create",
    {
      profile_root: profileRoot,
      name,
      base_currency: baseCurrency,
      starting_cash: startingCash
    },
    parsePortfolioDetail
  );
}

export async function recordAcquisition(
  profileRoot: string,
  portfolioId: string,
  instrumentId: string,
  quantity: string,
  unitPrice: string,
  currency: string,
  fee: string,
  sourceId: string
): Promise<PortfolioDetail> {
  return request(
    "portfolio.acquisition.record",
    {
      profile_root: profileRoot,
      portfolio_id: portfolioId,
      instrument_id: instrumentId,
      quantity,
      unit_price: unitPrice,
      currency,
      fee,
      source_id: sourceId
    },
    parsePortfolioDetail
  );
}

export async function recordValuation(
  profileRoot: string,
  portfolioId: string,
  assetId: string,
  quantity: string,
  unitPrice: string,
  priceCurrency: string,
  priceSource: string,
  priceEffectiveAt: string,
  valuationRevision: string
): Promise<PortfolioDetail> {
  return request(
    "portfolio.valuation.record",
    {
      profile_root: profileRoot,
      portfolio_id: portfolioId,
      asset_id: assetId,
      quantity,
      unit_price: unitPrice,
      price_currency: priceCurrency,
      price_source: priceSource,
      price_effective_at: priceEffectiveAt,
      valuation_revision: valuationRevision
    },
    parsePortfolioDetail
  );
}

async function request<T>(
  method: string,
  params: Record<string, unknown>,
  parse: (record: Record<string, unknown>) => T
): Promise<T> {
  const requestId = crypto.randomUUID();
  let raw: string;
  try {
    raw = await invoke<string>("desktop_request", {
      requestJson: JSON.stringify({
        protocol_version: "1.0",
        request_id: requestId,
        method,
        params
      })
    });
  } catch (error) {
    throw new DesktopClientError({
      code: "sidecar_unavailable",
      message: error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      retryable: true
    });
  }
  const envelope = parseEnvelope(JSON.parse(raw), requestId);
  if (envelope.status === "error") {
    throw new DesktopClientError(
      envelope.error ?? {
        code: "unknown_error",
        message: "The OSCA sidecar reported an unknown error.",
        retryable: false
      }
    );
  }
  if (!envelope.result) throw invalid("Portfolio response contained no result.");
  return parse(envelope.result);
}

function parseEnvelope(value: unknown, requestId: string): Envelope {
  const record = object(value, "desktop response");
  const responseRequestId = string(record.request_id, "request_id");
  if (responseRequestId !== requestId) throw invalid("Desktop response identity mismatch.");
  const status = string(record.status, "status");
  if (status !== "ok" && status !== "error") throw invalid("Invalid desktop response status.");
  return {
    protocol_version: string(record.protocol_version, "protocol_version"),
    request_id: responseRequestId,
    status,
    result: record.result == null ? null : object(record.result, "result"),
    error: record.error == null ? null : parseError(object(record.error, "error"))
  };
}

function parsePortfolioList(record: Record<string, unknown>): PortfolioList {
  return {
    portfolios: array(record.portfolios, "portfolios").map(parsePortfolio),
    network_access_enabled: falseValue(record.network_access_enabled, "network_access_enabled"),
    recommendations_enabled: falseValue(record.recommendations_enabled, "recommendations_enabled"),
    real_capital_execution_enabled: falseValue(
      record.real_capital_execution_enabled,
      "real_capital_execution_enabled"
    )
  };
}

function parsePortfolioDetail(record: Record<string, unknown>): PortfolioDetail {
  return {
    portfolio: parsePortfolio(object(record.portfolio, "portfolio")),
    projection: parseProjection(object(record.projection, "projection")),
    events: array(record.events ?? [], "events").map((value) => parseEvent(object(value, "event"))),
    journal: array(record.journal ?? [], "journal").map((value) =>
      parseJournal(object(value, "journal transaction"))
    ),
    valuations: array(record.valuations ?? [], "valuations").map((value) =>
      parseValuation(object(value, "valuation"))
    ),
    network_access_enabled: falseValue(record.network_access_enabled, "network_access_enabled"),
    recommendations_enabled: falseValue(record.recommendations_enabled, "recommendations_enabled"),
    broker_connections_enabled: falseValue(
      record.broker_connections_enabled,
      "broker_connections_enabled"
    ),
    autonomous_execution_enabled: falseValue(
      record.autonomous_execution_enabled,
      "autonomous_execution_enabled"
    ),
    live_order_execution: falseValue(record.live_order_execution, "live_order_execution"),
    real_capital_execution_enabled: falseValue(
      record.real_capital_execution_enabled,
      "real_capital_execution_enabled"
    )
  };
}

function parsePortfolio(value: unknown): VirtualPortfolio {
  const record = object(value, "portfolio");
  const status = string(record.status, "portfolio.status");
  if (status !== "active" && status !== "closed") throw invalid("Unknown portfolio status.");
  return {
    portfolio_id: string(record.portfolio_id, "portfolio.portfolio_id"),
    name: string(record.name, "portfolio.name"),
    base_currency: string(record.base_currency, "portfolio.base_currency"),
    status,
    created_at: string(record.created_at, "portfolio.created_at"),
    source_portfolio_id: nullableString(record.source_portfolio_id, "portfolio.source_portfolio_id"),
    source_revision: nullableNumber(record.source_revision, "portfolio.source_revision"),
    lineage_kind: nullableString(record.lineage_kind, "portfolio.lineage_kind")
  };
}

function parseProjection(record: Record<string, unknown>): PortfolioProjection {
  const health = string(record.health, "projection.health");
  if (health !== "healthy" && health !== "degraded") throw invalid("Unknown projection health.");
  return {
    portfolio_id: string(record.portfolio_id, "projection.portfolio_id"),
    revision: number(record.revision, "projection.revision"),
    base_currency: string(record.base_currency, "projection.base_currency"),
    cash_by_currency: decimalRecord(record.cash_by_currency, "projection.cash_by_currency"),
    positions: array(record.positions, "projection.positions").map(parsePosition),
    lots: array(record.lots, "projection.lots").map(parseLot),
    realized_pnl_by_currency: decimalRecord(
      record.realized_pnl_by_currency,
      "projection.realized_pnl_by_currency"
    ),
    income_by_currency: decimalRecord(record.income_by_currency, "projection.income_by_currency"),
    fees_by_currency: decimalRecord(record.fees_by_currency, "projection.fees_by_currency"),
    health,
    missing_evidence: array(record.missing_evidence, "projection.missing_evidence").map((item) =>
      string(item, "projection.missing_evidence item")
    ),
    equity_base: nullableString(record.equity_base, "projection.equity_base"),
    unrealized_pnl_base: nullableString(
      record.unrealized_pnl_base,
      "projection.unrealized_pnl_base"
    ),
    gross_exposure_base: nullableString(
      record.gross_exposure_base,
      "projection.gross_exposure_base"
    ),
    net_exposure_base: nullableString(record.net_exposure_base, "projection.net_exposure_base"),
    allocation_by_asset: decimalRecord(record.allocation_by_asset, "projection.allocation_by_asset")
  };
}

function parsePosition(value: unknown): PortfolioPosition {
  const record = object(value, "position");
  return {
    instrument_id: string(record.instrument_id, "position.instrument_id"),
    quantity: decimal(record.quantity, "position.quantity"),
    book_cost: decimal(record.book_cost, "position.book_cost"),
    currency: string(record.currency, "position.currency")
  };
}

function parseLot(value: unknown): PortfolioLot {
  const record = object(value, "lot");
  return {
    ...parsePosition(record),
    lot_id: string(record.lot_id, "lot.lot_id"),
    acquired_at: string(record.acquired_at, "lot.acquired_at")
  };
}

function parseEvent(record: Record<string, unknown>): AccountingEvent {
  return {
    event_id: string(record.event_id, "event.event_id"),
    sequence: number(record.sequence, "event.sequence"),
    event_type: string(record.event_type, "event.event_type"),
    effective_at: string(record.effective_at, "event.effective_at"),
    source_kind: string(record.source_kind, "event.source_kind"),
    source_id: string(record.source_id, "event.source_id"),
    content_digest: string(record.content_digest, "event.content_digest")
  };
}

function parseJournal(record: Record<string, unknown>): JournalTransaction {
  return {
    transaction_id: string(record.transaction_id, "journal.transaction_id"),
    event_id: string(record.event_id, "journal.event_id"),
    effective_at: string(record.effective_at, "journal.effective_at"),
    postings: array(record.postings, "journal.postings").map((value) => {
      const posting = object(value, "journal posting");
      const side = string(posting.side, "posting.side");
      if (side !== "debit" && side !== "credit") throw invalid("Unknown journal side.");
      return {
        posting_id: string(posting.posting_id, "posting.posting_id"),
        account_code: string(posting.account_code, "posting.account_code"),
        side,
        currency: string(posting.currency, "posting.currency"),
        amount: decimal(posting.amount, "posting.amount"),
        instrument_id: nullableString(posting.instrument_id, "posting.instrument_id")
      };
    })
  };
}

function parseValuation(record: Record<string, unknown>): ValuationObservation {
  return {
    observation_id: string(record.observation_id, "valuation.observation_id"),
    asset_id: string(record.asset_id, "valuation.asset_id"),
    quantity: decimal(record.quantity, "valuation.quantity"),
    unit_price: decimal(record.unit_price, "valuation.unit_price"),
    price_currency: string(record.price_currency, "valuation.price_currency"),
    price_source: string(record.price_source, "valuation.price_source"),
    price_effective_at: string(record.price_effective_at, "valuation.price_effective_at"),
    fx_rate_to_base: nullableString(record.fx_rate_to_base, "valuation.fx_rate_to_base"),
    fx_source: nullableString(record.fx_source, "valuation.fx_source"),
    fx_effective_at: nullableString(record.fx_effective_at, "valuation.fx_effective_at"),
    valuation_revision: string(record.valuation_revision, "valuation.valuation_revision")
  };
}

function parseError(record: Record<string, unknown>): DesktopErrorPayload {
  return {
    code: string(record.code, "error.code"),
    message: string(record.message, "error.message"),
    retryable: typeof record.retryable === "boolean" ? record.retryable : false
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw invalid(`${label} must be an object.`);
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw invalid(`${label} must be an array.`);
  return value;
}

function string(value: unknown, label: string): string {
  if (typeof value !== "string") throw invalid(`${label} must be a string.`);
  return value;
}

function decimal(value: unknown, label: string): string {
  if (typeof value === "string") return value;
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  throw invalid(`${label} must be a decimal string.`);
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw invalid(`${label} must be a number.`);
  return value;
}

function nullableString(value: unknown, label: string): string | null {
  return value == null ? null : string(value, label);
}

function nullableNumber(value: unknown, label: string): number | null {
  return value == null ? null : number(value, label);
}

function decimalRecord(value: unknown, label: string): Record<string, string> {
  const record = object(value, label);
  return Object.fromEntries(Object.entries(record).map(([key, item]) => [key, decimal(item, `${label}.${key}`)]));
}

function falseValue(value: unknown, label: string): false {
  if (value !== false) throw invalid(`${label} must remain false.`);
  return false;
}

function invalid(message: string): DesktopClientError {
  return new DesktopClientError({ code: "invalid_response", message, retryable: true });
}
