import { invoke } from "@tauri-apps/api/core";

export class StrategyClientError extends Error {
  constructor(readonly code: string, message: string, readonly retryable = false) {
    super(message);
    this.name = "StrategyClientError";
  }
}

export type ValidationFinding = { code: string; severity: string; message: string };
export type ValidationResult = { can_execute: boolean; findings: ValidationFinding[] };

export type StrategyVersion = {
  version_id: number;
  version_number: number;
  dsl: Record<string, unknown>;
  dsl_digest: string;
  validation: ValidationResult;
  summary: string;
  created_at: string;
};

export type StrategyDefinition = {
  strategy_id: number;
  strategy_uuid: string;
  name: string;
  objective: string;
  asset_id: string;
  timeframe: string;
  status: string;
  current_version: StrategyVersion | null;
  version_count: number;
  versions?: StrategyVersion[];
  created_at: string;
  updated_at: string;
};

export type BacktestResult = {
  result_id: number;
  result_uuid: string;
  status: string;
  fidelity_level: string;
  result_digest: string;
  evidence_path: string;
  assumptions: {
    initial_cash: number;
    fees_bps: number;
    slippage_bps: number;
    sizing_fraction: number;
    fidelity_disclosure: string;
  };
  metrics: {
    bars_processed: number;
    signal_bar_count: number;
    trade_count: number;
    exposure_bar_count: number;
    initial_cash: number;
    final_equity: number;
    strategy_return: number;
    buy_and_hold_return: number;
    max_drawdown: number;
  };
  equity_curve: BacktestPoint[];
  trades: BacktestTrade[];
  warnings: string[];
};

export type BacktestPoint = {
  timestamp: string;
  close: number;
  equity: number;
  drawdown: number;
  signal: string;
};

export type BacktestTrade = {
  timestamp: string;
  side: string;
  fill_price: number;
  quantity: number;
  fees: number;
  research_assumption: boolean;
};

export type BacktestExport = {
  result_id: number;
  manifest_path: string;
  manifest_sha256: string;
  data_paths: string[];
  thin_manifest: boolean;
  provider_datasets_embedded: boolean;
};

export type BacktestEvaluation = {
  evaluation_id: number;
  evaluation_type: string;
  status: string;
  result_digest: string;
  evidence_path: string;
  budget: Record<string, unknown>;
  rows: Record<string, unknown>[];
  partitions?: Record<string, unknown>[];
  warnings: string[];
};

export function listStrategies(profileRoot: string): Promise<StrategyDefinition[]> {
  return request("strategy.list", { profile_root: profileRoot }, (row) =>
    array(row.strategies, "strategies").map((item) => parseStrategy(object(item, "strategy")))
  );
}

export function createStrategy(
  profileRoot: string,
  name: string,
  objective: string,
  assetId: string,
  timeframe: string,
  dsl: Record<string, unknown>
): Promise<StrategyDefinition> {
  return request(
    "strategy.create",
    { profile_root: profileRoot, name, objective, asset_id: assetId, timeframe, dsl },
    (row) => parseStrategy(object(row.strategy, "strategy"))
  );
}

export function createStrategyVersion(
  profileRoot: string,
  strategyId: number,
  dsl: Record<string, unknown>,
  summary: string
): Promise<StrategyDefinition> {
  return request(
    "strategy.version.create",
    { profile_root: profileRoot, strategy_id: strategyId, dsl, summary },
    (row) => parseStrategy(object(row.strategy, "strategy"))
  );
}

export function validateStrategyDsl(
  profileRoot: string,
  dsl: Record<string, unknown>
): Promise<ValidationResult> {
  return request(
    "strategy.validate",
    { profile_root: profileRoot, dsl },
    (row) => parseValidation(object(row.validation, "validation"))
  );
}

export function runBacktest(
  profileRoot: string,
  strategyId: number,
  strategyVersionId: number,
  initialCash: number
): Promise<BacktestResult> {
  return request(
    "backtest.run",
    {
      profile_root: profileRoot,
      strategy_id: strategyId,
      strategy_version_id: strategyVersionId,
      initial_cash: initialCash
    },
    (row) => parseBacktest(object(row.result, "result"))
  );
}

export function prepareBacktestExport(profileRoot: string, resultId: number): Promise<BacktestExport> {
  return request(
    "backtest.export.prepare",
    { profile_root: profileRoot, result_id: resultId },
    (row) => ({
      result_id: number(row.result_id, "result_id"),
      manifest_path: text(row.manifest_path, "manifest_path"),
      manifest_sha256: text(row.manifest_sha256, "manifest_sha256"),
      data_paths: array(row.data_paths, "data_paths").map((item) => text(item, "data_path")),
      thin_manifest: Boolean(row.thin_manifest),
      provider_datasets_embedded: Boolean(row.provider_datasets_embedded)
    })
  );
}

export function runSensitivity(
  profileRoot: string,
  strategyId: number,
  strategyVersionId: number,
  parameter: "entry.window" | "exit.window",
  values: number[]
): Promise<BacktestEvaluation> {
  return request(
    "backtest.sensitivity.run",
    {
      profile_root: profileRoot,
      strategy_id: strategyId,
      strategy_version_id: strategyVersionId,
      parameter,
      values
    },
    (row) => parseEvaluation(object(row.evaluation, "evaluation"))
  );
}

export function runWalkforward(
  profileRoot: string,
  strategyId: number,
  strategyVersionId: number,
  trainFraction: number
): Promise<BacktestEvaluation> {
  return request(
    "backtest.walkforward.run",
    {
      profile_root: profileRoot,
      strategy_id: strategyId,
      strategy_version_id: strategyVersionId,
      train_fraction: trainFraction
    },
    (row) => parseEvaluation(object(row.evaluation, "evaluation"))
  );
}

export function cancelEvaluation(profileRoot: string, evaluationId: number): Promise<BacktestEvaluation> {
  return request(
    "backtest.cancel",
    { profile_root: profileRoot, evaluation_id: evaluationId },
    (row) => parseEvaluation(object(row.evaluation, "evaluation"))
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
      requestJson: JSON.stringify({ protocol_version: "1.0", request_id: requestId, method, params })
    });
  } catch (error) {
    throw new StrategyClientError(
      "sidecar_unavailable",
      error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      true
    );
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new StrategyClientError("invalid_response", "Desktop response identity did not match.", true);
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new StrategyClientError(
      text(failure.code, "error.code"),
      text(failure.message, "error.message"),
      Boolean(failure.retryable)
    );
  }
  return parse(object(envelope.result, "result"));
}

function parseStrategy(row: Record<string, unknown>): StrategyDefinition {
  return {
    strategy_id: number(row.strategy_id, "strategy_id"),
    strategy_uuid: text(row.strategy_uuid, "strategy_uuid"),
    name: text(row.name, "name"),
    objective: text(row.objective, "objective"),
    asset_id: text(row.asset_id, "asset_id"),
    timeframe: text(row.timeframe, "timeframe"),
    status: text(row.status, "status"),
    current_version: row.current_version == null ? null : parseVersion(object(row.current_version, "current_version")),
    version_count: number(row.version_count, "version_count"),
    versions: row.versions == null ? undefined : array(row.versions, "versions").map((item) => parseVersion(object(item, "version"))),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function parseVersion(row: Record<string, unknown>): StrategyVersion {
  return {
    version_id: number(row.version_id, "version_id"),
    version_number: number(row.version_number, "version_number"),
    dsl: object(row.dsl, "dsl"),
    dsl_digest: text(row.dsl_digest, "dsl_digest"),
    validation: parseValidation(object(row.validation, "validation")),
    summary: text(row.summary, "summary"),
    created_at: text(row.created_at, "created_at")
  };
}

function parseValidation(row: Record<string, unknown>): ValidationResult {
  return {
    can_execute: Boolean(row.can_execute),
    findings: array(row.findings, "findings").map((item) => {
      const finding = object(item, "finding");
      return {
        code: text(finding.code, "finding.code"),
        severity: text(finding.severity, "finding.severity"),
        message: text(finding.message, "finding.message")
      };
    })
  };
}

function parseBacktest(row: Record<string, unknown>): BacktestResult {
  return {
    result_id: number(row.result_id, "result_id"),
    result_uuid: text(row.result_uuid, "result_uuid"),
    status: text(row.status, "status"),
    fidelity_level: text(row.fidelity_level, "fidelity_level"),
    result_digest: text(row.result_digest, "result_digest"),
    evidence_path: text(row.evidence_path, "evidence_path"),
    assumptions: parseAssumptions(object(row.assumptions, "assumptions")),
    metrics: parseMetrics(object(row.metrics, "metrics")),
    equity_curve: array(row.equity_curve, "equity_curve").map((item) => parsePoint(object(item, "equity_curve point"))),
    trades: array(row.trades, "trades").map((item) => parseTrade(object(item, "trade"))),
    warnings: array(row.warnings, "warnings").map((item) => text(item, "warning"))
  };
}

function parsePoint(row: Record<string, unknown>): BacktestPoint {
  return {
    timestamp: text(row.timestamp, "point.timestamp"),
    close: number(row.close, "point.close"),
    equity: number(row.equity, "point.equity"),
    drawdown: number(row.drawdown, "point.drawdown"),
    signal: text(row.signal, "point.signal")
  };
}

function parseTrade(row: Record<string, unknown>): BacktestTrade {
  return {
    timestamp: text(row.timestamp, "trade.timestamp"),
    side: text(row.side, "trade.side"),
    fill_price: number(row.fill_price, "trade.fill_price"),
    quantity: number(row.quantity, "trade.quantity"),
    fees: number(row.fees, "trade.fees"),
    research_assumption: Boolean(row.research_assumption)
  };
}

function parseAssumptions(row: Record<string, unknown>): BacktestResult["assumptions"] {
  return {
    initial_cash: number(row.initial_cash, "initial_cash"),
    fees_bps: number(row.fees_bps, "fees_bps"),
    slippage_bps: number(row.slippage_bps, "slippage_bps"),
    sizing_fraction: number(row.sizing_fraction, "sizing_fraction"),
    fidelity_disclosure: text(row.fidelity_disclosure, "fidelity_disclosure")
  };
}

function parseMetrics(row: Record<string, unknown>): BacktestResult["metrics"] {
  return {
    bars_processed: number(row.bars_processed, "bars_processed"),
    signal_bar_count: number(row.signal_bar_count, "signal_bar_count"),
    trade_count: number(row.trade_count, "trade_count"),
    exposure_bar_count: number(row.exposure_bar_count, "exposure_bar_count"),
    initial_cash: number(row.initial_cash, "initial_cash"),
    final_equity: number(row.final_equity, "final_equity"),
    strategy_return: number(row.strategy_return, "strategy_return"),
    buy_and_hold_return: number(row.buy_and_hold_return, "buy_and_hold_return"),
    max_drawdown: number(row.max_drawdown, "max_drawdown")
  };
}

function parseEvaluation(row: Record<string, unknown>): BacktestEvaluation {
  return {
    evaluation_id: number(row.evaluation_id, "evaluation_id"),
    evaluation_type: text(row.evaluation_type, "evaluation_type"),
    status: text(row.status, "evaluation.status"),
    result_digest: text(row.result_digest, "evaluation.result_digest"),
    evidence_path: text(row.evidence_path, "evaluation.evidence_path"),
    budget: object(row.budget, "evaluation.budget"),
    rows: array(row.rows, "evaluation.rows").map((item) => object(item, "evaluation.row")),
    partitions: row.partitions == null ? undefined : array(row.partitions, "evaluation.partitions").map((item) => object(item, "partition")),
    warnings: array(row.warnings, "evaluation.warnings").map((item) => text(item, "evaluation.warning"))
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new StrategyClientError("invalid_response", `${label} must be an object.`, true);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new StrategyClientError("invalid_response", `${label} must be an array.`, true);
  }
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new StrategyClientError("invalid_response", `${label} must be a string.`, true);
  }
  return value;
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new StrategyClientError("invalid_response", `${label} must be a number.`, true);
  }
  return value;
}
