import { invoke } from "@tauri-apps/api/core";
import {
  WorkbenchClientError,
  WorkbenchDerivedRequest,
  WorkbenchRange
} from "./workbenchApi";

export type QuantitativePoint = {
  timestamp: string;
  close: number;
  rsi: number | null;
  atr: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  bollinger_middle: number | null;
  bollinger_upper: number | null;
  bollinger_lower: number | null;
  drawdown: number;
  trend_regime: string;
  volatility_regime: string;
};

export type QuantitativeAnalysis = {
  asset_id: string;
  dataset_revision_id: string;
  source_point_count: number;
  displayed_point_count: number;
  display_method: string;
  summary: Record<string, number | null>;
  parameters: Record<string, number>;
  points: QuantitativePoint[];
  input_digest: string;
  output_digest: string;
  point_in_time_safe: boolean;
};

export type ComparisonResult = {
  primary: { asset_id: string; symbol: string; currency: string; timeframe: string };
  comparison: { asset_id: string; symbol: string; currency: string; timeframe: string };
  aligned_return_count: number;
  correlation: number | null;
  beta: number | null;
  rolling_window: number;
  normalization_basis: string;
  points: Array<{
    timestamp: string;
    primary_return: number;
    benchmark_return: number;
    rolling_correlation: number | null;
  }>;
};

export type WorkbenchExport = {
  export_id: string;
  row_count: number;
  csv_path: string;
  metadata_path: string;
  csv_sha256: string;
  display_downsampling_was_active: boolean;
  full_resolution: true;
};

export type SavedWorkbenchView = {
  view_id: number;
  name: string;
  description: string | null;
  config_version: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export function getQuantitativeAnalysis(
  profileRoot: string,
  assetId: string,
  timeframe: string,
  maxRows = 240,
  parameters: Record<string, number> = {},
  range: WorkbenchRange = {}
): Promise<QuantitativeAnalysis> {
  return request("workbench.analysis.get", {
    profile_root: profileRoot,
    asset_id: assetId,
    timeframe,
    max_rows: maxRows,
    parameters,
    ...rangeParams(range)
  }, parseAnalysis);
}

export function getComparison(
  profileRoot: string,
  primaryAssetId: string,
  comparisonAssetId: string,
  timeframe: string,
  rollingWindow = 20,
  maxRows = 240,
  range: WorkbenchRange = {}
): Promise<ComparisonResult> {
  return request("workbench.comparison.get", {
    profile_root: profileRoot,
    primary_asset_id: primaryAssetId,
    comparison_asset_id: comparisonAssetId,
    timeframe,
    rolling_window: rollingWindow,
    max_rows: maxRows,
    ...rangeParams(range)
  }, parseComparison);
}

export function prepareWorkbenchExport(
  profileRoot: string,
  assetId: string,
  timeframe: string,
  maxRows: number,
  derived: WorkbenchDerivedRequest[],
  range: WorkbenchRange = {}
): Promise<WorkbenchExport> {
  return request("workbench.export.prepare", {
    profile_root: profileRoot,
    asset_id: assetId,
    timeframe,
    max_rows: maxRows,
    derived,
    ...rangeParams(range)
  }, (row) => ({
    export_id: text(row.export_id, "export_id"),
    row_count: number(row.row_count, "row_count"),
    csv_path: text(row.csv_path, "csv_path"),
    metadata_path: text(row.metadata_path, "metadata_path"),
    csv_sha256: text(row.csv_sha256, "csv_sha256"),
    display_downsampling_was_active: Boolean(row.display_downsampling_was_active),
    full_resolution: true
  }));
}

export function listWorkbenchViews(profileRoot: string): Promise<SavedWorkbenchView[]> {
  return request("workbench.view.list", { profile_root: profileRoot }, (row) =>
    array(row.views, "views").map((item) => parseView(object(item, "view")))
  );
}

export function createWorkbenchView(
  profileRoot: string,
  name: string,
  description: string | null,
  config: Record<string, unknown>
): Promise<SavedWorkbenchView> {
  return request("workbench.view.create", {
    profile_root: profileRoot,
    name,
    description,
    config
  }, (row) => parseView(object(row.view, "view")));
}

export function updateWorkbenchView(
  profileRoot: string,
  viewId: number,
  description: string | null,
  config: Record<string, unknown>
): Promise<SavedWorkbenchView> {
  return request("workbench.view.update", {
    profile_root: profileRoot,
    view_id: viewId,
    description,
    config
  }, (row) => parseView(object(row.view, "view")));
}

export function renameWorkbenchView(
  profileRoot: string,
  viewId: number,
  name: string
): Promise<SavedWorkbenchView> {
  return request("workbench.view.rename", {
    profile_root: profileRoot,
    view_id: viewId,
    name
  }, (row) => parseView(object(row.view, "view")));
}

export function deleteWorkbenchView(profileRoot: string, viewId: number): Promise<void> {
  return request(
    "workbench.view.delete",
    { profile_root: profileRoot, view_id: viewId },
    () => undefined
  );
}

function rangeParams(range: WorkbenchRange): Record<string, string> {
  return {
    ...(range.start ? { start: range.start } : {}),
    ...(range.end ? { end: range.end } : {})
  };
}

async function request<T>(
  method: string,
  params: Record<string, unknown>,
  parse: (value: Record<string, unknown>) => T
): Promise<T> {
  const requestId = crypto.randomUUID();
  let raw: string;
  try {
    raw = await invoke<string>("desktop_request", {
      requestJson: JSON.stringify({ protocol_version: "1.0", request_id: requestId, method, params })
    });
  } catch (error) {
    throw new WorkbenchClientError(
      "sidecar_unavailable",
      error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      true
    );
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new WorkbenchClientError(
      "invalid_response",
      "Desktop response identity did not match the request.",
      true
    );
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new WorkbenchClientError(
      text(failure.code, "error.code"),
      text(failure.message, "error.message"),
      Boolean(failure.retryable)
    );
  }
  return parse(object(envelope.result, "result"));
}

function parseAnalysis(row: Record<string, unknown>): QuantitativeAnalysis {
  const rawSummary = object(row.summary, "summary");
  const summary: Record<string, number | null> = {};
  for (const [key, value] of Object.entries(rawSummary)) {
    summary[key] = value == null ? null : number(value, `summary.${key}`);
  }
  const rawParameters = object(row.parameters, "parameters");
  const parameters: Record<string, number> = {};
  for (const [key, value] of Object.entries(rawParameters)) {
    parameters[key] = number(value, `parameters.${key}`);
  }
  return {
    asset_id: text(row.asset_id, "asset_id"),
    dataset_revision_id: text(row.dataset_revision_id, "dataset_revision_id"),
    source_point_count: number(row.source_point_count, "source_point_count"),
    displayed_point_count: number(row.displayed_point_count, "displayed_point_count"),
    display_method: text(row.display_method, "display_method"),
    summary,
    parameters,
    points: array(row.points, "points").map((item) => parseQuantPoint(object(item, "point"))),
    input_digest: text(row.input_digest, "input_digest"),
    output_digest: text(row.output_digest, "output_digest"),
    point_in_time_safe: Boolean(row.point_in_time_safe)
  };
}

function parseQuantPoint(row: Record<string, unknown>): QuantitativePoint {
  return {
    timestamp: text(row.timestamp, "timestamp"),
    close: number(row.close, "close"),
    rsi: nullableNumber(row.rsi, "rsi"),
    atr: nullableNumber(row.atr, "atr"),
    macd: nullableNumber(row.macd, "macd"),
    macd_signal: nullableNumber(row.macd_signal, "macd_signal"),
    macd_histogram: nullableNumber(row.macd_histogram, "macd_histogram"),
    bollinger_middle: nullableNumber(row.bollinger_middle, "bollinger_middle"),
    bollinger_upper: nullableNumber(row.bollinger_upper, "bollinger_upper"),
    bollinger_lower: nullableNumber(row.bollinger_lower, "bollinger_lower"),
    drawdown: number(row.drawdown, "drawdown"),
    trend_regime: text(row.trend_regime, "trend_regime"),
    volatility_regime: text(row.volatility_regime, "volatility_regime")
  };
}

function parseComparison(row: Record<string, unknown>): ComparisonResult {
  const primary = object(row.primary, "primary");
  const comparison = object(row.comparison, "comparison");
  return {
    primary: parseComparisonAsset(primary),
    comparison: parseComparisonAsset(comparison),
    aligned_return_count: number(row.aligned_return_count, "aligned_return_count"),
    correlation: nullableNumber(row.correlation, "correlation"),
    beta: nullableNumber(row.beta, "beta"),
    rolling_window: number(row.rolling_window, "rolling_window"),
    normalization_basis: text(row.normalization_basis, "normalization_basis"),
    points: array(row.points, "points").map((item) => {
      const point = object(item, "comparison point");
      return {
        timestamp: text(point.timestamp, "timestamp"),
        primary_return: number(point.primary_return, "primary_return"),
        benchmark_return: number(point.benchmark_return, "benchmark_return"),
        rolling_correlation: nullableNumber(point.rolling_correlation, "rolling_correlation")
      };
    })
  };
}

function parseComparisonAsset(row: Record<string, unknown>) {
  return {
    asset_id: text(row.asset_id, "asset_id"),
    symbol: text(row.symbol, "symbol"),
    currency: text(row.currency, "currency"),
    timeframe: text(row.timeframe, "timeframe")
  };
}

function parseView(row: Record<string, unknown>): SavedWorkbenchView {
  return {
    view_id: number(row.view_id, "view_id"),
    name: text(row.name, "name"),
    description: row.description == null ? null : text(row.description, "description"),
    config_version: text(row.config_version, "config_version"),
    config: object(row.config, "config"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new WorkbenchClientError("invalid_response", `${label} must be an object.`, true);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new WorkbenchClientError("invalid_response", `${label} must be an array.`, true);
  }
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new WorkbenchClientError("invalid_response", `${label} must be a string.`, true);
  }
  return value;
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new WorkbenchClientError("invalid_response", `${label} must be a number.`, true);
  }
  return value;
}

function nullableNumber(value: unknown, label: string): number | null {
  return value == null ? null : number(value, label);
}
