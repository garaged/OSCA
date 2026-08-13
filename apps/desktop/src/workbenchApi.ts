import { invoke } from "@tauri-apps/api/core";

export type WorkbenchDerivedRequest = {
  kind: "simple_return" | "log_return" | "sma" | "ema" | "rolling_volatility" | "rolling_volume";
  window?: number;
};

export type WorkbenchRange = {
  start?: string;
  end?: string;
};

export type WorkbenchRow = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  derived: Record<string, number | null>;
};

export type WorkbenchSeries = {
  asset_id: string;
  dataset: {
    dataset_revision_id: string;
    symbol: string;
    timeframe: string;
    source_kind: string;
    source_attribution: string;
    retained_row_count: number | null;
    effective_end: string;
  };
  series: {
    source_row_count: number;
    filtered_row_count: number;
    returned_row_count: number;
    first_timestamp: string;
    last_timestamp: string;
    downsampling_method: string;
    downsampling_preserves_first_last: boolean;
    payload_sha256: string;
    rows: WorkbenchRow[];
    derived_evidence: Array<{
      series_id: string;
      kind: string;
      window: number | null;
      warmup_rows: number;
      point_in_time_safe: boolean;
      input_digest: string;
      output_digest: string;
    }>;
  };
  network_access_enabled: false;
  recommendations_enabled: false;
  broker_connections_enabled: false;
  real_capital_execution_enabled: false;
};

export class WorkbenchClientError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly retryable = false
  ) {
    super(message);
    this.name = "WorkbenchClientError";
  }
}

export function getWorkbenchSeries(
  profileRoot: string,
  assetId: string,
  timeframe: string,
  maxRows: number,
  derived: WorkbenchDerivedRequest[],
  range: WorkbenchRange = {}
): Promise<WorkbenchSeries> {
  return request(
    "workbench.series.get",
    {
      profile_root: profileRoot,
      asset_id: assetId,
      timeframe,
      max_rows: maxRows,
      derived,
      ...(range.start ? { start: range.start } : {}),
      ...(range.end ? { end: range.end } : {})
    },
    parseWorkbenchSeries
  );
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
      requestJson: JSON.stringify({
        protocol_version: "1.0",
        request_id: requestId,
        method,
        params
      })
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

function parseWorkbenchSeries(row: Record<string, unknown>): WorkbenchSeries {
  const dataset = object(row.dataset, "dataset");
  const series = object(row.series, "series");
  return {
    asset_id: text(row.asset_id, "asset_id"),
    dataset: {
      dataset_revision_id: text(dataset.dataset_revision_id, "dataset_revision_id"),
      symbol: text(dataset.symbol, "symbol"),
      timeframe: text(dataset.timeframe, "timeframe"),
      source_kind: text(dataset.source_kind, "source_kind"),
      source_attribution: text(dataset.source_attribution, "source_attribution"),
      retained_row_count: nullableNumber(dataset.retained_row_count, "retained_row_count"),
      effective_end: text(dataset.effective_end, "effective_end")
    },
    series: {
      source_row_count: number(series.source_row_count, "source_row_count"),
      filtered_row_count: number(series.filtered_row_count, "filtered_row_count"),
      returned_row_count: number(series.returned_row_count, "returned_row_count"),
      first_timestamp: text(series.first_timestamp, "first_timestamp"),
      last_timestamp: text(series.last_timestamp, "last_timestamp"),
      downsampling_method: text(series.downsampling_method, "downsampling_method"),
      downsampling_preserves_first_last: Boolean(series.downsampling_preserves_first_last),
      payload_sha256: text(series.payload_sha256, "payload_sha256"),
      rows: array(series.rows, "rows").map(parseRow),
      derived_evidence: array(series.derived_evidence, "derived_evidence").map((value) => {
        const evidence = object(value, "derived_evidence");
        return {
          series_id: text(evidence.series_id, "series_id"),
          kind: text(evidence.kind, "kind"),
          window: nullableNumber(evidence.window, "window"),
          warmup_rows: number(evidence.warmup_rows, "warmup_rows"),
          point_in_time_safe: Boolean(evidence.point_in_time_safe),
          input_digest: text(evidence.input_digest, "input_digest"),
          output_digest: text(evidence.output_digest, "output_digest")
        };
      })
    },
    network_access_enabled: false,
    recommendations_enabled: false,
    broker_connections_enabled: false,
    real_capital_execution_enabled: false
  };
}

function parseRow(value: unknown): WorkbenchRow {
  const row = object(value, "row");
  const rawDerived = object(row.derived, "derived");
  const derived: Record<string, number | null> = {};
  for (const [key, item] of Object.entries(rawDerived)) {
    derived[key] = nullableNumber(item, `derived.${key}`);
  }
  return {
    timestamp: text(row.timestamp, "timestamp"),
    open: number(row.open, "open"),
    high: number(row.high, "high"),
    low: number(row.low, "low"),
    close: number(row.close, "close"),
    volume: number(row.volume, "volume"),
    derived
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
