import { invoke } from "@tauri-apps/api/core";

export class MLLabClientError extends Error {
  constructor(readonly code: string, message: string, readonly retryable = false) {
    super(message);
    this.name = "MLLabClientError";
  }
}

export type MLFeatureDefinition = {
  feature_id: string;
  version: number;
  name: string;
  value_type: string;
  lookback_bars: number | string;
  transformation: string;
  point_in_time_safe: boolean;
  missing_data_behavior: string;
};

export type MLLabelDefinition = {
  label_id: string;
  version: number;
  task: string;
  description: string;
  leakage_checked: boolean;
};

export type MLCatalog = {
  features: MLFeatureDefinition[];
  labels: MLLabelDefinition[];
};

export type MLExperiment = {
  experiment_id: string;
  name: string;
  status: string;
  definition: Record<string, unknown>;
  result: Record<string, unknown> | null;
  output_digest: string | null;
  error: { code: string; message: string } | null;
  cancel_requested: boolean;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
  events: Array<{ event_type: string; details: Record<string, unknown>; created_at: string }>;
  research_only: true;
  automatic_promotion_enabled: false;
  recommendations_enabled: false;
  broker_execution_enabled: false;
  real_capital_execution_enabled: false;
};

export type MLExperimentInput = {
  name: string;
  assetId: string;
  timeframe: string;
  task: "regression" | "classification";
  model: string;
  horizon: number;
  featureWindow: number;
  trainFraction: number;
  validationFraction: number;
  embargo: number;
  iterations: number;
};

export function listMLCatalog(profileRoot: string): Promise<MLCatalog> {
  return request("ml.catalog.list", { profile_root: profileRoot }, (row) => ({
    features: array(row.features, "features").map((item) => parseFeature(object(item, "feature"))),
    labels: array(row.labels, "labels").map((item) => parseLabel(object(item, "label")))
  }));
}

export function listMLExperiments(profileRoot: string): Promise<MLExperiment[]> {
  return request("ml.experiment.list", { profile_root: profileRoot }, (row) =>
    array(row.experiments, "experiments").map((item) => parseExperiment(object(item, "experiment")))
  );
}

export function createMLExperiment(profileRoot: string, input: MLExperimentInput): Promise<MLExperiment> {
  return request(
    "ml.experiment.create",
    {
      profile_root: profileRoot,
      name: input.name,
      asset_id: input.assetId,
      timeframe: input.timeframe,
      task: input.task,
      model: input.model,
      horizon: input.horizon,
      feature_window: input.featureWindow,
      train_fraction: input.trainFraction,
      validation_fraction: input.validationFraction,
      embargo: input.embargo,
      iterations: input.iterations,
      feature_ids: ["return.last.v1", "return.mean.v1", "return.volatility.v1"],
      survivorship_policy: "single_asset_no_universe_selection",
      corporate_action_policy: "governed_dataset_semantics",
      missing_data_policy: "fail_closed"
    },
    (row) => parseExperiment(object(row.experiment, "experiment"))
  );
}

export function runMLExperiment(profileRoot: string, experimentId: string): Promise<MLExperiment> {
  return request(
    "ml.experiment.run",
    { profile_root: profileRoot, experiment_id: experimentId },
    (row) => parseExperiment(object(row.experiment, "experiment"))
  );
}

export function cancelMLExperiment(profileRoot: string, experimentId: string): Promise<MLExperiment> {
  return request(
    "ml.experiment.cancel",
    { profile_root: profileRoot, experiment_id: experimentId },
    (row) => parseExperiment(object(row.experiment, "experiment"))
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
    throw new MLLabClientError(
      "sidecar_unavailable",
      error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      true
    );
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new MLLabClientError("invalid_response", "Desktop response identity did not match.", true);
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new MLLabClientError(
      text(failure.code, "error.code"),
      text(failure.message, "error.message"),
      Boolean(failure.retryable)
    );
  }
  return parse(object(envelope.result, "result"));
}

function parseFeature(row: Record<string, unknown>): MLFeatureDefinition {
  const lookback = row.lookback_bars;
  if (typeof lookback !== "number" && typeof lookback !== "string") {
    throw new MLLabClientError("invalid_response", "feature.lookback_bars is invalid", true);
  }
  return {
    feature_id: text(row.feature_id, "feature_id"),
    version: number(row.version, "feature.version"),
    name: text(row.name, "feature.name"),
    value_type: text(row.value_type, "feature.value_type"),
    lookback_bars: lookback,
    transformation: text(row.transformation, "feature.transformation"),
    point_in_time_safe: Boolean(row.point_in_time_safe),
    missing_data_behavior: text(row.missing_data_behavior, "feature.missing_data_behavior")
  };
}

function parseLabel(row: Record<string, unknown>): MLLabelDefinition {
  return {
    label_id: text(row.label_id, "label_id"),
    version: number(row.version, "label.version"),
    task: text(row.task, "label.task"),
    description: text(row.description, "label.description"),
    leakage_checked: Boolean(row.leakage_checked)
  };
}

function parseExperiment(row: Record<string, unknown>): MLExperiment {
  const error = row.error == null ? null : object(row.error, "experiment.error");
  return {
    experiment_id: text(row.experiment_id, "experiment_id"),
    name: text(row.name, "experiment.name"),
    status: text(row.status, "experiment.status"),
    definition: object(row.definition, "experiment.definition"),
    result: row.result == null ? null : object(row.result, "experiment.result"),
    output_digest: nullableText(row.output_digest, "experiment.output_digest"),
    error: error == null ? null : { code: text(error.code, "error.code"), message: text(error.message, "error.message") },
    cancel_requested: Boolean(row.cancel_requested),
    created_at: text(row.created_at, "experiment.created_at"),
    started_at: nullableText(row.started_at, "experiment.started_at"),
    completed_at: nullableText(row.completed_at, "experiment.completed_at"),
    updated_at: text(row.updated_at, "experiment.updated_at"),
    events: array(row.events, "experiment.events").map((item) => {
      const event = object(item, "experiment.event");
      return {
        event_type: text(event.event_type, "event.event_type"),
        details: object(event.details, "event.details"),
        created_at: text(event.created_at, "event.created_at")
      };
    }),
    research_only: true,
    automatic_promotion_enabled: false,
    recommendations_enabled: false,
    broker_execution_enabled: false,
    real_capital_execution_enabled: false
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new MLLabClientError("invalid_response", `${label} must be an object.`, true);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw new MLLabClientError("invalid_response", `${label} must be an array.`, true);
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") throw new MLLabClientError("invalid_response", `${label} must be a string.`, true);
  return value;
}

function nullableText(value: unknown, label: string): string | null {
  return value == null ? null : text(value, label);
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new MLLabClientError("invalid_response", `${label} must be a number.`, true);
  }
  return value;
}
