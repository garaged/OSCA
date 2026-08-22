import { invoke } from "@tauri-apps/api/core";
import { DesktopClientError, DesktopErrorPayload } from "./api";

export type PaperSafety = {
  network_access_enabled: false;
  recommendations_enabled: false;
  broker_connections_enabled: false;
  autonomous_execution_enabled: false;
  live_order_execution: false;
  real_capital_execution_enabled: false;
};

export type PaperRunBinding = {
  paper_run_id: string;
  paper_account_id: string;
  portfolio_id: string;
  approved_candidate_id: string | null;
  created_at: string;
};

export type PaperDraft = {
  draft_id: string;
  draft_version: number;
  paper_run_id: string;
  paper_account_id: string;
  portfolio_id: string;
  source_kind: string;
  source_id: string;
  instrument_id: string;
  timeframe: string;
  currency: string;
  dataset_revision_id: string | null;
  side: "buy" | "sell";
  order_type: "market" | "limit" | "stop" | "scheduled_market";
  quantity: string;
  limit_price: string | null;
  stop_price: string | null;
  scheduled_at: string | null;
  expires_at: string | null;
  assumption_id: string;
  lot_allocations: Record<string, string>;
  created_at: string;
};

export type PaperOrder = {
  order_id: string;
  draft_id: string;
  draft_version: number;
  paper_run_id: string;
  paper_account_id: string;
  portfolio_id: string;
  instrument_id: string;
  timeframe: string;
  currency: string;
  dataset_revision_id: string | null;
  side: "buy" | "sell";
  order_type: string;
  quantity: string;
  limit_price: string | null;
  stop_price: string | null;
  scheduled_at: string | null;
  expires_at: string | null;
  assumption_id: string;
  confirmed_at: string;
  eligible_at: string;
  status: string;
};

export type PaperLifecycle = {
  event_id: string;
  order_id: string;
  sequence: number;
  status: string;
  source_id: string;
  reason: string;
  fill_id: string | null;
  effective_at: string;
};

export type PaperFill = {
  fill_id: string;
  order_id: string;
  sequence: number;
  bar_evidence_id: string;
  dataset_revision_id: string;
  assumption_id: string;
  instrument_id: string;
  side: "buy" | "sell";
  quantity: string;
  execution_price: string;
  fee: string;
  effective_at: string;
};

export type PaperOrderRow = {
  order: PaperOrder;
  status: string;
  remaining_quantity: string;
  lifecycle: PaperLifecycle[];
  fills: PaperFill[];
};

export type PaperCheckpoint = {
  paper_run_id: string;
  sequence_number: number;
  idempotency_key: string;
  last_processed_at: string;
  source_event_ids: string[];
  created_at: string;
};

export type PaperRunInspection = PaperSafety & {
  binding: PaperRunBinding;
  drafts: PaperDraft[];
  orders: PaperOrderRow[];
  checkpoint: PaperCheckpoint | null;
  projection: {
    revision: number;
    cash_by_currency: Record<string, string>;
    positions: Array<{
      instrument_id: string;
      quantity: string;
      book_cost: string;
      currency: string;
    }>;
    health: "healthy" | "degraded";
    missing_evidence: string[];
    equity_base: string | null;
    unrealized_pnl_base: string | null;
  };
};

export type PaperAssumptionInput = {
  assumptionId: string;
  spreadBps: string;
  slippageBps: string;
  feeBps: string;
  flatFee: string;
  latencyMs: number;
  maxVolumeParticipation: string;
  maxOrderNotional?: string;
  maxPositionNotional?: string;
};

export type PaperDraftInput = {
  draftId: string;
  draftVersion: number;
  paperRunId: string;
  paperAccountId: string;
  portfolioId: string;
  sourceId: string;
  instrumentId: string;
  timeframe: string;
  currency: string;
  datasetRevisionId?: string;
  side: "buy" | "sell";
  orderType: "market" | "limit" | "stop" | "scheduled_market";
  quantity: string;
  limitPrice?: string;
  stopPrice?: string;
  scheduledAt?: string;
  expiresAt?: string;
  assumptionId: string;
  lotAllocations?: Record<string, string>;
};

export type PaperBarInput = {
  evidenceId: string;
  instrumentId: string;
  datasetRevisionId: string;
  marketSourceId: string;
  timeframe: string;
  barStartedAt: string;
  barEndedAt: string;
  availableAt: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume?: string;
  complete: boolean;
  marketCalendarId?: string;
  sessionOpen: boolean;
};

export type ComparisonMetricInput = {
  name: string;
  backtestValue: string;
  forwardValue: string;
  unit: string;
  methodology: string;
};

type Envelope = {
  request_id: string;
  status: "ok" | "error";
  result: Record<string, unknown> | null;
  error: DesktopErrorPayload | null;
};

export async function bindPaperRun(
  profileRoot: string,
  paperRunId: string,
  paperAccountId: string,
  portfolioId: string
): Promise<PaperRunBinding & PaperSafety> {
  return request("paper.run.bind", {
    profile_root: profileRoot,
    paper_run_id: paperRunId,
    paper_account_id: paperAccountId,
    portfolio_id: portfolioId
  }, (record) => ({
    ...parseSafety(record),
    ...parseBinding(object(record.binding, "binding"))
  }));
}

export async function retainPaperAssumptions(
  profileRoot: string,
  input: PaperAssumptionInput
): Promise<PaperSafety> {
  return request("paper.assumptions.retain", {
    profile_root: profileRoot,
    assumption_id: input.assumptionId,
    spread_bps: input.spreadBps,
    slippage_bps: input.slippageBps,
    fee_bps: input.feeBps,
    flat_fee: input.flatFee,
    latency_ms: input.latencyMs,
    max_volume_participation: input.maxVolumeParticipation,
    require_volume: true,
    ...(input.maxOrderNotional ? { max_order_notional: input.maxOrderNotional } : {}),
    ...(input.maxPositionNotional
      ? { max_position_notional: input.maxPositionNotional }
      : {})
  }, parseSafety);
}

export async function retainPaperDraft(
  profileRoot: string,
  input: PaperDraftInput
): Promise<PaperDraft & PaperSafety> {
  return request("paper.order.draft.retain", {
    profile_root: profileRoot,
    draft_id: input.draftId,
    draft_version: input.draftVersion,
    paper_run_id: input.paperRunId,
    paper_account_id: input.paperAccountId,
    portfolio_id: input.portfolioId,
    source_kind: "manual",
    source_id: input.sourceId,
    instrument_id: input.instrumentId,
    timeframe: input.timeframe,
    currency: input.currency,
    ...(input.datasetRevisionId ? { dataset_revision_id: input.datasetRevisionId } : {}),
    side: input.side,
    order_type: input.orderType,
    quantity: input.quantity,
    ...(input.limitPrice ? { limit_price: input.limitPrice } : {}),
    ...(input.stopPrice ? { stop_price: input.stopPrice } : {}),
    ...(input.scheduledAt ? { scheduled_at: input.scheduledAt } : {}),
    ...(input.expiresAt ? { expires_at: input.expiresAt } : {}),
    assumption_id: input.assumptionId,
    lot_allocations: input.lotAllocations ?? {}
  }, (record) => ({
    ...parseSafety(record),
    ...parseDraft(object(record.draft, "draft"))
  }));
}

export async function confirmPaperDraft(
  profileRoot: string,
  paperRunId: string,
  draftId: string,
  draftVersion: number
): Promise<{ order: PaperOrder; simulated_only: true } & PaperSafety> {
  return request("paper.order.confirm", {
    profile_root: profileRoot,
    paper_run_id: paperRunId,
    draft_id: draftId,
    draft_version: draftVersion,
    confirmed_at: new Date().toISOString()
  }, (record) => ({
    ...parseSafety(record),
    simulated_only: trueValue(record.simulated_only, "simulated_only"),
    order: parseOrder(object(record.order, "order"))
  }));
}

export async function inspectPaperRun(
  profileRoot: string,
  paperRunId: string
): Promise<PaperRunInspection> {
  return request("paper.run.inspect", {
    profile_root: profileRoot,
    paper_run_id: paperRunId
  }, parseInspection);
}

export async function cancelPaperOrder(
  profileRoot: string,
  orderId: string,
  reason: string
): Promise<PaperSafety> {
  return request("paper.order.cancel", {
    profile_root: profileRoot,
    order_id: orderId,
    source_id: `paper-lab-cancel:${crypto.randomUUID()}`,
    reason,
    effective_at: new Date().toISOString()
  }, parseSafety);
}

export async function processPaperBar(
  profileRoot: string,
  paperRunId: string,
  paperAccountId: string,
  orderId: string,
  input: PaperBarInput
): Promise<Record<string, unknown> & PaperSafety> {
  return request("paper.order.process_bar", {
    profile_root: profileRoot,
    paper_run_id: paperRunId,
    paper_account_id: paperAccountId,
    order_id: orderId,
    data_status: "healthy",
    operational_status: "healthy",
    ...barParams(input)
  }, (record) => ({ ...record, ...parseSafety(record) }));
}

export async function appendPaperMark(
  profileRoot: string,
  portfolioId: string,
  priceCurrency: string,
  input: PaperBarInput
): Promise<Record<string, unknown> & PaperSafety> {
  return request("paper.mark.append", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    price_currency: priceCurrency,
    ...barParams(input)
  }, (record) => ({ ...record, ...parseSafety(record) }));
}

export async function recordPaperCheckpoint(
  profileRoot: string,
  paperRunId: string,
  input: PaperBarInput
): Promise<PaperCheckpoint & PaperSafety> {
  return request("paper.checkpoint.record", {
    profile_root: profileRoot,
    paper_run_id: paperRunId,
    idempotency_key: `paper-bar:${input.evidenceId}`,
    last_processed_at: input.availableAt,
    source_event_ids: [input.evidenceId]
  }, (record) => ({
    ...parseSafety(record),
    ...parseCheckpoint(object(record.checkpoint, "checkpoint"))
  }));
}

export async function buildPaperComparison(
  profileRoot: string,
  input: {
    backtestResultId: number;
    paperRunId: string;
    strategyVersionId: number;
    assumptionId: string;
    backtestStartedAt: string;
    backtestEndedAt: string;
    forwardStartedAt: string;
    forwardEndedAt: string;
    metrics: ComparisonMetricInput[];
    methodologyDifferences: string[];
  }
): Promise<Record<string, unknown> & PaperSafety> {
  return request("paper.comparison.build", {
    profile_root: profileRoot,
    backtest_result_id: input.backtestResultId,
    paper_run_id: input.paperRunId,
    strategy_version_id: input.strategyVersionId,
    assumption_id: input.assumptionId,
    backtest_started_at: input.backtestStartedAt,
    backtest_ended_at: input.backtestEndedAt,
    forward_started_at: input.forwardStartedAt,
    forward_ended_at: input.forwardEndedAt,
    compared_at: new Date().toISOString(),
    metrics: input.metrics.map((metric) => ({
      name: metric.name,
      backtest_value: metric.backtestValue,
      forward_value: metric.forwardValue,
      unit: metric.unit,
      methodology: metric.methodology
    })),
    methodology_differences: input.methodologyDifferences
  }, (record) => ({ ...record, ...parseSafety(record) }));
}

function barParams(input: PaperBarInput): Record<string, unknown> {
  return {
    evidence_id: input.evidenceId,
    instrument_id: input.instrumentId,
    dataset_revision_id: input.datasetRevisionId,
    market_source_id: input.marketSourceId,
    timeframe: input.timeframe,
    bar_started_at: input.barStartedAt,
    bar_ended_at: input.barEndedAt,
    available_at: input.availableAt,
    open: input.open,
    high: input.high,
    low: input.low,
    close: input.close,
    ...(input.volume ? { volume: input.volume } : {}),
    complete: input.complete,
    ...(input.marketCalendarId ? { market_calendar_id: input.marketCalendarId } : {}),
    session_open: input.sessionOpen
  };
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
  if (!envelope.result) throw invalid("Paper response contained no result.");
  return parse(envelope.result);
}

function parseEnvelope(value: unknown, requestId: string): Envelope {
  const record = object(value, "desktop response");
  const responseRequestId = string(record.request_id, "request_id");
  if (responseRequestId !== requestId) throw invalid("Desktop response identity mismatch.");
  const status = string(record.status, "status");
  if (status !== "ok" && status !== "error") throw invalid("Invalid desktop response status.");
  return {
    request_id: responseRequestId,
    status,
    result: record.result == null ? null : object(record.result, "result"),
    error: record.error == null ? null : parseError(object(record.error, "error"))
  };
}

function parseInspection(record: Record<string, unknown>): PaperRunInspection {
  return {
    ...parseSafety(record),
    binding: parseBinding(object(record.binding, "binding")),
    drafts: array(record.drafts, "drafts").map((value) => parseDraft(object(value, "draft"))),
    orders: array(record.orders, "orders").map((value) => parseOrderRow(object(value, "order row"))),
    checkpoint:
      record.checkpoint == null ? null : parseCheckpoint(object(record.checkpoint, "checkpoint")),
    projection: parseProjection(object(record.projection, "projection"))
  };
}

function parseSafety(record: Record<string, unknown>): PaperSafety {
  return {
    network_access_enabled: falseValue(record.network_access_enabled, "network_access_enabled"),
    recommendations_enabled: falseValue(record.recommendations_enabled, "recommendations_enabled"),
    broker_connections_enabled: falseValue(record.broker_connections_enabled, "broker_connections_enabled"),
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

function parseBinding(record: Record<string, unknown>): PaperRunBinding {
  return {
    paper_run_id: string(record.paper_run_id, "paper_run_id"),
    paper_account_id: string(record.paper_account_id, "paper_account_id"),
    portfolio_id: string(record.portfolio_id, "portfolio_id"),
    approved_candidate_id: nullableString(record.approved_candidate_id, "approved_candidate_id"),
    created_at: string(record.created_at, "created_at")
  };
}

function parseDraft(record: Record<string, unknown>): PaperDraft {
  return {
    draft_id: string(record.draft_id, "draft_id"),
    draft_version: number(record.draft_version, "draft_version"),
    paper_run_id: string(record.paper_run_id, "paper_run_id"),
    paper_account_id: string(record.paper_account_id, "paper_account_id"),
    portfolio_id: string(record.portfolio_id, "portfolio_id"),
    source_kind: string(record.source_kind, "source_kind"),
    source_id: string(record.source_id, "source_id"),
    instrument_id: string(record.instrument_id, "instrument_id"),
    timeframe: string(record.timeframe, "timeframe"),
    currency: string(record.currency, "currency"),
    dataset_revision_id: nullableString(record.dataset_revision_id, "dataset_revision_id"),
    side: enumValue(record.side, ["buy", "sell"] as const, "side"),
    order_type: enumValue(
      record.order_type,
      ["market", "limit", "stop", "scheduled_market"] as const,
      "order_type"
    ),
    quantity: decimalString(record.quantity, "quantity"),
    limit_price: nullableDecimal(record.limit_price, "limit_price"),
    stop_price: nullableDecimal(record.stop_price, "stop_price"),
    scheduled_at: nullableString(record.scheduled_at, "scheduled_at"),
    expires_at: nullableString(record.expires_at, "expires_at"),
    assumption_id: string(record.assumption_id, "assumption_id"),
    lot_allocations: decimalRecord(record.lot_allocations, "lot_allocations"),
    created_at: string(record.created_at, "created_at")
  };
}

function parseOrder(record: Record<string, unknown>): PaperOrder {
  return {
    order_id: string(record.order_id, "order_id"),
    draft_id: string(record.draft_id, "draft_id"),
    draft_version: number(record.draft_version, "draft_version"),
    paper_run_id: string(record.paper_run_id, "paper_run_id"),
    paper_account_id: string(record.paper_account_id, "paper_account_id"),
    portfolio_id: string(record.portfolio_id, "portfolio_id"),
    instrument_id: string(record.instrument_id, "instrument_id"),
    timeframe: string(record.timeframe, "timeframe"),
    currency: string(record.currency, "currency"),
    dataset_revision_id: nullableString(record.dataset_revision_id, "dataset_revision_id"),
    side: enumValue(record.side, ["buy", "sell"] as const, "side"),
    order_type: string(record.order_type, "order_type"),
    quantity: decimalString(record.quantity, "quantity"),
    limit_price: nullableDecimal(record.limit_price, "limit_price"),
    stop_price: nullableDecimal(record.stop_price, "stop_price"),
    scheduled_at: nullableString(record.scheduled_at, "scheduled_at"),
    expires_at: nullableString(record.expires_at, "expires_at"),
    assumption_id: string(record.assumption_id, "assumption_id"),
    confirmed_at: string(record.confirmed_at, "confirmed_at"),
    eligible_at: string(record.eligible_at, "eligible_at"),
    status: string(record.status, "status")
  };
}

function parseOrderRow(record: Record<string, unknown>): PaperOrderRow {
  return {
    order: parseOrder(object(record.order, "order")),
    status: string(record.status, "status"),
    remaining_quantity: decimalString(record.remaining_quantity, "remaining_quantity"),
    lifecycle: array(record.lifecycle, "lifecycle").map((value) =>
      parseLifecycle(object(value, "lifecycle event"))
    ),
    fills: array(record.fills, "fills").map((value) => parseFill(object(value, "fill")))
  };
}

function parseLifecycle(record: Record<string, unknown>): PaperLifecycle {
  return {
    event_id: string(record.event_id, "event_id"),
    order_id: string(record.order_id, "order_id"),
    sequence: number(record.sequence, "sequence"),
    status: string(record.status, "status"),
    source_id: string(record.source_id, "source_id"),
    reason: string(record.reason, "reason"),
    fill_id: nullableString(record.fill_id, "fill_id"),
    effective_at: string(record.effective_at, "effective_at")
  };
}

function parseFill(record: Record<string, unknown>): PaperFill {
  return {
    fill_id: string(record.fill_id, "fill_id"),
    order_id: string(record.order_id, "order_id"),
    sequence: number(record.sequence, "sequence"),
    bar_evidence_id: string(record.bar_evidence_id, "bar_evidence_id"),
    dataset_revision_id: string(record.dataset_revision_id, "dataset_revision_id"),
    assumption_id: string(record.assumption_id, "assumption_id"),
    instrument_id: string(record.instrument_id, "instrument_id"),
    side: enumValue(record.side, ["buy", "sell"] as const, "side"),
    quantity: decimalString(record.quantity, "quantity"),
    execution_price: decimalString(record.execution_price, "execution_price"),
    fee: decimalString(record.fee, "fee"),
    effective_at: string(record.effective_at, "effective_at")
  };
}

function parseCheckpoint(record: Record<string, unknown>): PaperCheckpoint {
  return {
    paper_run_id: string(record.paper_run_id, "paper_run_id"),
    sequence_number: number(record.sequence_number, "sequence_number"),
    idempotency_key: string(record.idempotency_key, "idempotency_key"),
    last_processed_at: string(record.last_processed_at, "last_processed_at"),
    source_event_ids: array(record.source_event_ids, "source_event_ids").map((value) =>
      string(value, "source_event_id")
    ),
    created_at: string(record.created_at, "created_at")
  };
}

function parseProjection(record: Record<string, unknown>): PaperRunInspection["projection"] {
  return {
    revision: number(record.revision, "revision"),
    cash_by_currency: decimalRecord(record.cash_by_currency, "cash_by_currency"),
    positions: array(record.positions, "positions").map((value) => {
      const position = object(value, "position");
      return {
        instrument_id: string(position.instrument_id, "instrument_id"),
        quantity: decimalString(position.quantity, "quantity"),
        book_cost: decimalString(position.book_cost, "book_cost"),
        currency: string(position.currency, "currency")
      };
    }),
    health: enumValue(record.health, ["healthy", "degraded"] as const, "health"),
    missing_evidence: array(record.missing_evidence, "missing_evidence").map((value) =>
      string(value, "missing evidence")
    ),
    equity_base: nullableDecimal(record.equity_base, "equity_base"),
    unrealized_pnl_base: nullableDecimal(record.unrealized_pnl_base, "unrealized_pnl_base")
  };
}

function parseError(record: Record<string, unknown>): DesktopErrorPayload {
  return {
    code: string(record.code, "error.code"),
    message: string(record.message, "error.message"),
    retryable: boolean(record.retryable, "error.retryable")
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw invalid(`${label} is invalid.`);
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw invalid(`${label} must be an array.`);
  return value;
}

function string(value: unknown, label: string): string {
  if (typeof value !== "string") throw invalid(`${label} must be text.`);
  return value;
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value)) throw invalid(`${label} must be an integer.`);
  return value;
}

function boolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") throw invalid(`${label} must be boolean.`);
  return value;
}

function falseValue(value: unknown, label: string): false {
  if (value !== false) throw invalid(`${label} must remain disabled.`);
  return false;
}

function trueValue(value: unknown, label: string): true {
  if (value !== true) throw invalid(`${label} must be true.`);
  return true;
}

function nullableString(value: unknown, label: string): string | null {
  return value == null ? null : string(value, label);
}

function decimalString(value: unknown, label: string): string {
  const text = string(value, label);
  if (!text.trim() || !Number.isFinite(Number(text))) throw invalid(`${label} must be exact decimal text.`);
  return text;
}

function nullableDecimal(value: unknown, label: string): string | null {
  return value == null ? null : decimalString(value, label);
}

function decimalRecord(value: unknown, label: string): Record<string, string> {
  const record = object(value ?? {}, label);
  return Object.fromEntries(
    Object.entries(record).map(([key, raw]) => [key, decimalString(raw, `${label}.${key}`)])
  );
}

function enumValue<const T extends readonly string[]>(
  value: unknown,
  allowed: T,
  label: string
): T[number] {
  const text = string(value, label);
  if (!allowed.includes(text)) throw invalid(`${label} is unsupported.`);
  return text as T[number];
}

function invalid(message: string): DesktopClientError {
  return new DesktopClientError({ code: "invalid_response", message, retryable: false });
}
