import { invoke } from "@tauri-apps/api/core";
import { DesktopClientError, DesktopErrorPayload } from "./api";

export type PerformancePoint = {
  snapshot_id: string;
  captured_at: string;
  equity_base: string;
  cumulative_return: string;
  drawdown: string;
};

export type PerformanceReport = {
  portfolio_id: string;
  base_currency: string;
  evidence_start: string;
  evidence_end: string;
  snapshot_count: number;
  cumulative_return: string;
  max_drawdown: string;
  points: PerformancePoint[];
  recommendations_enabled: false;
};

export type AttributionItem = {
  instrument_id: string;
  market_value_base: string;
  book_cost_base: string;
  unrealized_pnl_base: string;
  allocation: string;
  price_source: string;
  price_effective_at: string;
  fx_source: string | null;
  fx_effective_at: string | null;
};

export type AttributionReport = {
  portfolio_id: string;
  base_currency: string;
  health: "healthy" | "degraded";
  missing_evidence: string[];
  items: AttributionItem[];
  recommendations_enabled: false;
};

export type AnalyticsReport = {
  snapshot_count: number;
  performance: PerformanceReport | null;
  attribution: AttributionReport;
  network_access_enabled: false;
  recommendations_enabled: false;
  real_capital_execution_enabled: false;
};

export type ScenarioReport = {
  portfolio_id: string;
  base_currency: string;
  baseline_equity: string;
  scenario_equity: string;
  equity_change: string;
  shocked_unrealized_pnl: string;
  gross_exposure: string;
  asset_shocks: Record<string, string>;
  fx_shocks: Record<string, string>;
  mutated_portfolio: false;
  recommendations_enabled: false;
};

export type BenchmarkComparison = {
  portfolio_id: string;
  evidence_start: string;
  evidence_end: string;
  portfolio_return: string;
  benchmark_return: string;
  excess_return: string;
  benchmark_source_ids: string[];
  descriptive_only: true;
  recommendations_enabled: false;
};

type Envelope = {
  request_id: string;
  status: "ok" | "error";
  result: Record<string, unknown> | null;
  error: DesktopErrorPayload | null;
};

export async function captureAnalyticsSnapshot(
  profileRoot: string,
  portfolioId: string
): Promise<void> {
  await request(
    "portfolio.analytics.snapshot.capture",
    {
      profile_root: profileRoot,
      portfolio_id: portfolioId,
      captured_at: new Date().toISOString()
    },
    () => undefined
  );
}

export async function getAnalyticsReport(
  profileRoot: string,
  portfolioId: string
): Promise<AnalyticsReport> {
  return request(
    "portfolio.analytics.report",
    { profile_root: profileRoot, portfolio_id: portfolioId },
    parseAnalyticsReport
  );
}

export async function runPortfolioScenario(
  profileRoot: string,
  portfolioId: string,
  assetShocks: Record<string, string>,
  fxShocks: Record<string, string>
): Promise<ScenarioReport> {
  return request(
    "portfolio.analytics.scenario",
    {
      profile_root: profileRoot,
      portfolio_id: portfolioId,
      asset_shocks: assetShocks,
      fx_shocks: fxShocks
    },
    (record) => parseScenario(object(record.scenario, "scenario"))
  );
}

export async function comparePortfolioBenchmark(
  profileRoot: string,
  portfolioId: string,
  benchmark: Array<{ observed_at: string; value: string; source_id: string }>
): Promise<BenchmarkComparison> {
  return request(
    "portfolio.analytics.benchmark",
    { profile_root: profileRoot, portfolio_id: portfolioId, benchmark },
    (record) => parseBenchmark(object(record.comparison, "comparison"))
  );
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
    throw invalid("Desktop analytics response was not valid JSON.");
  }
  const envelope = parseEnvelope(decoded, requestId);
  if (envelope.status === "error") {
    throw new DesktopClientError(
      envelope.error ?? {
        code: "unknown_error",
        message: "The OSCA sidecar reported an unknown analytics error.",
        retryable: false
      }
    );
  }
  if (!envelope.result) throw invalid("Desktop analytics response contained no result.");
  return parse(envelope.result);
}

function parseEnvelope(value: unknown, requestId: string): Envelope {
  const record = object(value, "desktop response");
  const responseRequestId = text(record.request_id, "request_id");
  if (responseRequestId !== requestId) throw invalid("Desktop response identity mismatch.");
  const status = text(record.status, "status");
  if (status !== "ok" && status !== "error") throw invalid("Invalid desktop response status.");
  return {
    request_id: responseRequestId,
    status,
    result: record.result == null ? null : object(record.result, "result"),
    error: record.error == null ? null : parseError(object(record.error, "error"))
  };
}

function parseAnalyticsReport(record: Record<string, unknown>): AnalyticsReport {
  return {
    snapshot_count: number(record.snapshot_count, "snapshot_count"),
    performance:
      record.performance == null ? null : parsePerformance(object(record.performance, "performance")),
    attribution: parseAttribution(object(record.attribution, "attribution")),
    network_access_enabled: falseValue(record.network_access_enabled, "network_access_enabled"),
    recommendations_enabled: falseValue(record.recommendations_enabled, "recommendations_enabled"),
    real_capital_execution_enabled: falseValue(
      record.real_capital_execution_enabled,
      "real_capital_execution_enabled"
    )
  };
}

function parsePerformance(record: Record<string, unknown>): PerformanceReport {
  return {
    portfolio_id: text(record.portfolio_id, "performance.portfolio_id"),
    base_currency: text(record.base_currency, "performance.base_currency"),
    evidence_start: text(record.evidence_start, "performance.evidence_start"),
    evidence_end: text(record.evidence_end, "performance.evidence_end"),
    snapshot_count: number(record.snapshot_count, "performance.snapshot_count"),
    cumulative_return: decimal(record.cumulative_return, "performance.cumulative_return"),
    max_drawdown: decimal(record.max_drawdown, "performance.max_drawdown"),
    points: array(record.points, "performance.points").map((value) => {
      const point = object(value, "performance point");
      return {
        snapshot_id: text(point.snapshot_id, "point.snapshot_id"),
        captured_at: text(point.captured_at, "point.captured_at"),
        equity_base: decimal(point.equity_base, "point.equity_base"),
        cumulative_return: decimal(point.cumulative_return, "point.cumulative_return"),
        drawdown: decimal(point.drawdown, "point.drawdown")
      };
    }),
    recommendations_enabled: falseValue(
      record.recommendations_enabled,
      "performance.recommendations_enabled"
    )
  };
}

function parseAttribution(record: Record<string, unknown>): AttributionReport {
  const health = text(record.health, "attribution.health");
  if (health !== "healthy" && health !== "degraded") throw invalid("Unknown attribution health.");
  return {
    portfolio_id: text(record.portfolio_id, "attribution.portfolio_id"),
    base_currency: text(record.base_currency, "attribution.base_currency"),
    health,
    missing_evidence: array(record.missing_evidence, "attribution.missing_evidence").map((item) =>
      text(item, "attribution missing evidence")
    ),
    items: array(record.items, "attribution.items").map((value) => {
      const item = object(value, "attribution item");
      return {
        instrument_id: text(item.instrument_id, "attribution.instrument_id"),
        market_value_base: decimal(item.market_value_base, "attribution.market_value_base"),
        book_cost_base: decimal(item.book_cost_base, "attribution.book_cost_base"),
        unrealized_pnl_base: decimal(
          item.unrealized_pnl_base,
          "attribution.unrealized_pnl_base"
        ),
        allocation: decimal(item.allocation, "attribution.allocation"),
        price_source: text(item.price_source, "attribution.price_source"),
        price_effective_at: text(item.price_effective_at, "attribution.price_effective_at"),
        fx_source: nullableText(item.fx_source, "attribution.fx_source"),
        fx_effective_at: nullableText(item.fx_effective_at, "attribution.fx_effective_at")
      };
    }),
    recommendations_enabled: falseValue(
      record.recommendations_enabled,
      "attribution.recommendations_enabled"
    )
  };
}

function parseScenario(record: Record<string, unknown>): ScenarioReport {
  return {
    portfolio_id: text(record.portfolio_id, "scenario.portfolio_id"),
    base_currency: text(record.base_currency, "scenario.base_currency"),
    baseline_equity: decimal(record.baseline_equity, "scenario.baseline_equity"),
    scenario_equity: decimal(record.scenario_equity, "scenario.scenario_equity"),
    equity_change: decimal(record.equity_change, "scenario.equity_change"),
    shocked_unrealized_pnl: decimal(
      record.shocked_unrealized_pnl,
      "scenario.shocked_unrealized_pnl"
    ),
    gross_exposure: decimal(record.gross_exposure, "scenario.gross_exposure"),
    asset_shocks: decimalRecord(record.asset_shocks, "scenario.asset_shocks"),
    fx_shocks: decimalRecord(record.fx_shocks, "scenario.fx_shocks"),
    mutated_portfolio: falseValue(record.mutated_portfolio, "scenario.mutated_portfolio"),
    recommendations_enabled: falseValue(
      record.recommendations_enabled,
      "scenario.recommendations_enabled"
    )
  };
}

function parseBenchmark(record: Record<string, unknown>): BenchmarkComparison {
  return {
    portfolio_id: text(record.portfolio_id, "benchmark.portfolio_id"),
    evidence_start: text(record.evidence_start, "benchmark.evidence_start"),
    evidence_end: text(record.evidence_end, "benchmark.evidence_end"),
    portfolio_return: decimal(record.portfolio_return, "benchmark.portfolio_return"),
    benchmark_return: decimal(record.benchmark_return, "benchmark.benchmark_return"),
    excess_return: decimal(record.excess_return, "benchmark.excess_return"),
    benchmark_source_ids: array(record.benchmark_source_ids, "benchmark.source_ids").map((item) =>
      text(item, "benchmark source id")
    ),
    descriptive_only: trueValue(record.descriptive_only, "benchmark.descriptive_only"),
    recommendations_enabled: falseValue(
      record.recommendations_enabled,
      "benchmark.recommendations_enabled"
    )
  };
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

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw invalid(`${label} must be an array.`);
  return value;
}

function text(value: unknown, label: string): string {
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

function nullableText(value: unknown, label: string): string | null {
  return value == null ? null : text(value, label);
}

function decimalRecord(value: unknown, label: string): Record<string, string> {
  const record = object(value, label);
  return Object.fromEntries(
    Object.entries(record).map(([key, item]) => [key, decimal(item, `${label}.${key}`)])
  );
}

function falseValue(value: unknown, label: string): false {
  if (value !== false) throw invalid(`${label} must remain false.`);
  return false;
}

function trueValue(value: unknown, label: string): true {
  if (value !== true) throw invalid(`${label} must remain true.`);
  return true;
}

function invalid(message: string): DesktopClientError {
  return new DesktopClientError({ code: "invalid_response", message, retryable: true });
}
