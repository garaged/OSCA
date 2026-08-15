import { invoke } from "@tauri-apps/api/core";
import { DesktopClientError, DesktopErrorPayload } from "./api";

export type PortfolioExportResult = {
  portfolio_id: string;
  output_path: string;
  content_digest: string;
  provider_data_embedded: false;
};

export async function recordDisposal(
  profileRoot: string,
  portfolioId: string,
  input: {
    instrumentId: string;
    quantity: string;
    unitPrice: string;
    currency: string;
    fee: string;
    sourceId: string;
    lotAllocations?: Record<string, string>;
  }
): Promise<string> {
  return mutate("portfolio.disposal.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    instrument_id: input.instrumentId,
    quantity: input.quantity,
    unit_price: input.unitPrice,
    currency: input.currency,
    fee: input.fee,
    source_id: input.sourceId,
    ...(input.lotAllocations ? { lot_allocations: input.lotAllocations } : {})
  });
}

export async function recordDividend(
  profileRoot: string,
  portfolioId: string,
  instrumentId: string,
  amount: string,
  currency: string,
  sourceId: string
): Promise<string> {
  return mutate("portfolio.dividend.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    instrument_id: instrumentId,
    amount,
    currency,
    source_id: sourceId
  });
}

export async function recordSplit(
  profileRoot: string,
  portfolioId: string,
  instrumentId: string,
  factor: string,
  sourceId: string
): Promise<string> {
  return mutate("portfolio.split.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    instrument_id: instrumentId,
    factor,
    source_id: sourceId
  });
}

export async function recordFork(
  profileRoot: string,
  portfolioId: string,
  input: {
    sourceInstrumentId: string;
    newInstrumentId: string;
    newQuantity: string;
    currency: string;
    allocatedBookCost: string;
    sourceId: string;
    sourceLotAllocations?: Record<string, string>;
  }
): Promise<string> {
  return mutate("portfolio.fork.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    source_instrument_id: input.sourceInstrumentId,
    new_instrument_id: input.newInstrumentId,
    new_quantity: input.newQuantity,
    currency: input.currency,
    allocated_book_cost: input.allocatedBookCost,
    source_id: input.sourceId,
    ...(input.sourceLotAllocations
      ? { source_lot_allocations: input.sourceLotAllocations }
      : {})
  });
}

export async function recordFxConversion(
  profileRoot: string,
  portfolioId: string,
  fromCurrency: string,
  fromAmount: string,
  toCurrency: string,
  toAmount: string,
  sourceId: string
): Promise<string> {
  return mutate("portfolio.fx.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    from_currency: fromCurrency,
    from_amount: fromAmount,
    to_currency: toCurrency,
    to_amount: toAmount,
    source_id: sourceId
  });
}

export async function reverseAccountingEvent(
  profileRoot: string,
  portfolioId: string,
  originalEventId: string,
  reason: string,
  sourceId: string
): Promise<string> {
  return mutate("portfolio.reversal.record", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    original_event_id: originalEventId,
    reason,
    source_id: sourceId
  });
}

export async function clonePortfolio(
  profileRoot: string,
  portfolioId: string,
  name: string
): Promise<string> {
  return mutate("portfolio.clone", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    name
  });
}

export async function resetPortfolio(
  profileRoot: string,
  portfolioId: string,
  name: string,
  startingCash: string
): Promise<string> {
  return mutate("portfolio.reset", {
    profile_root: profileRoot,
    portfolio_id: portfolioId,
    name,
    starting_cash: startingCash
  });
}

export async function preparePortfolioExport(
  profileRoot: string,
  portfolioId: string
): Promise<PortfolioExportResult> {
  return request(
    "portfolio.export.prepare",
    { profile_root: profileRoot, portfolio_id: portfolioId },
    (record) => ({
      portfolio_id: text(record.portfolio_id, "portfolio_id"),
      output_path: text(record.output_path, "output_path"),
      content_digest: text(record.content_digest, "content_digest"),
      provider_data_embedded: falseValue(
        record.provider_data_embedded,
        "provider_data_embedded"
      )
    })
  );
}

export async function restorePortfolio(
  profileRoot: string,
  inputPath: string
): Promise<string> {
  return request(
    "portfolio.restore",
    { profile_root: profileRoot, input_path: inputPath },
    portfolioIdFromResult
  );
}

async function mutate(method: string, params: Record<string, unknown>): Promise<string> {
  return request(method, params, portfolioIdFromResult);
}

async function request<T>(
  method: string,
  params: Record<string, unknown>,
  parse: (result: Record<string, unknown>) => T
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
  let decoded: unknown;
  try {
    decoded = JSON.parse(raw);
  } catch {
    throw invalid("Desktop portfolio operation response was not valid JSON.");
  }
  const envelope = object(decoded, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw invalid("Desktop response identity mismatch.");
  }
  const status = text(envelope.status, "status");
  if (status === "error") {
    const error = envelope.error == null ? null : parseError(object(envelope.error, "error"));
    throw new DesktopClientError(
      error ?? {
        code: "unknown_error",
        message: "The OSCA sidecar reported an unknown portfolio operation error.",
        retryable: false
      }
    );
  }
  if (status !== "ok") throw invalid("Invalid desktop response status.");
  if (envelope.result == null) throw invalid("Desktop portfolio operation returned no result.");
  return parse(object(envelope.result, "result"));
}

function portfolioIdFromResult(record: Record<string, unknown>): string {
  const portfolio = object(record.portfolio, "portfolio");
  return text(portfolio.portfolio_id, "portfolio.portfolio_id");
}

function parseError(record: Record<string, unknown>): DesktopErrorPayload {
  return {
    code: text(record.code, "error.code"),
    message: text(record.message, "error.message"),
    retryable: typeof record.retryable === "boolean" ? record.retryable : false
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw invalid(`${label} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") throw invalid(`${label} must be a string.`);
  return value;
}

function falseValue(value: unknown, label: string): false {
  if (value !== false) throw invalid(`${label} must remain false.`);
  return false;
}

function invalid(message: string): DesktopClientError {
  return new DesktopClientError({ code: "invalid_response", message, retryable: true });
}
