import { invoke } from "@tauri-apps/api/core";

export type ProviderRow = {
  provider_id: string;
  admission_status: string;
  approved_resources: string[];
  d3_acquisition_resources: string[];
  internal_use_only: boolean;
  redistribution_enabled: boolean;
  credential_mode: string;
  credential_reference: string | null;
  credential_state: string;
  credential_code: string;
  credential_remediation: string | null;
  network_required: boolean;
  acquisition_available: boolean;
  available_actions: string[];
  evidence_reviewed_at: string;
  rationale: string;
  findings: string[];
  promotion_automatic: boolean;
};

export type ProviderCatalog = {
  providers: ProviderRow[];
  offline_paths: Array<{
    id: string;
    label: string;
    network_required: boolean;
    credential_required: boolean;
    available: boolean;
  }>;
  network_consent_mode: string;
  provider_promotion_automatic: boolean;
  recommendations_enabled: boolean;
  live_execution_enabled: boolean;
};

export type CredentialResult = {
  operation: string;
  provider_id: string;
  reference: string;
  state: string;
  code: string;
  remediation: string | null;
  admission_status: string;
  acquisition_available: boolean;
  provider_promotion_automatic: boolean;
  secret_value_returned: false;
  deleted?: boolean;
};

export type LocalImportRequest = {
  profile_root: string;
  input_path: string;
  symbol: string;
  timeframe: string;
  source_uri?: string;
  calendar_assumption?: string;
};

export type LocalImportResult = {
  status: string;
  network_access_enabled: false;
  credential_required: false;
  provider_account_required: false;
  import: Record<string, unknown>;
};

export type AcquisitionRequest = {
  profile_root: string;
  provider_id: "kraken";
  asset_class: "crypto";
  symbol: string;
  timeframe: string;
  network_access_enabled: boolean;
  expected_pair_key?: string;
  minimum_rows?: number;
  freshness_max_age_seconds?: number;
};

export type AcquisitionEvidence = {
  acquisition_id: string;
  request_id: string;
  job_id: string;
  job_status: string;
  status: string;
  provider_id: string;
  symbol: string;
  timeframe: string;
  progress_percent: number;
  dataset_revision_id: string | null;
  canonical_row_count: number | null;
  source_attribution: string;
  quota_state: string;
  retry_after_seconds: number | null;
  reuse_state: string;
  rationale: string;
  remediation: string[];
  findings: string[];
  recommendations_enabled: false;
  broker_execution_enabled: false;
  real_capital_execution_enabled: false;
};

export class DataSourcesClientError extends Error {
  readonly code: string;
  readonly retryable: boolean;

  constructor(code: string, message: string, retryable = false) {
    super(message);
    this.name = "DataSourcesClientError";
    this.code = code;
    this.retryable = retryable;
  }
}

export function fetchProviderCatalog(): Promise<ProviderCatalog> {
  return request("provider.catalog", {}, parseCatalog);
}

export function storeProviderCredential(providerId: string, secretValue: string): Promise<CredentialResult> {
  return request("credential.store", { provider_id: providerId, secret_value: secretValue }, parseCredential);
}

export function probeProviderCredential(providerId: string): Promise<CredentialResult> {
  return request("credential.probe", { provider_id: providerId }, parseCredential);
}

export function deleteProviderCredential(providerId: string): Promise<CredentialResult> {
  return request("credential.delete", { provider_id: providerId }, parseCredential);
}

export function importLocalOhlcv(value: LocalImportRequest): Promise<LocalImportResult> {
  return request("local.import", value, (record) => ({
    status: text(record.status, "status"),
    network_access_enabled: false,
    credential_required: false,
    provider_account_required: false,
    import: object(record.import, "import")
  }));
}

export function submitKrakenAcquisition(value: AcquisitionRequest): Promise<AcquisitionEvidence> {
  return request("acquisition.run", value, (record) =>
    parseEvidence(object(record.evidence, "evidence"))
  );
}

export function listAcquisitionEvidence(profileRoot: string): Promise<AcquisitionEvidence[]> {
  return request("acquisition.list", { profile_root: profileRoot }, (record) =>
    array(record.evidence, "evidence").map((item) => parseEvidence(object(item, "evidence item")))
  );
}

async function request<T>(method: string, params: Record<string, unknown>, parse: (value: Record<string, unknown>) => T): Promise<T> {
  const requestId = crypto.randomUUID();
  let raw: string;
  try {
    raw = await invoke<string>("desktop_request", {
      requestJson: JSON.stringify({ protocol_version: "1.0", request_id: requestId, method, params })
    });
  } catch (error) {
    throw new DataSourcesClientError("sidecar_unavailable", error instanceof Error ? error.message : "The OSCA sidecar is unavailable.", true);
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new DataSourcesClientError("invalid_response", "Desktop response identity did not match the request.", true);
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new DataSourcesClientError(text(failure.code, "error.code"), text(failure.message, "error.message"), Boolean(failure.retryable));
  }
  return parse(object(envelope.result, "result"));
}

function parseCatalog(record: Record<string, unknown>): ProviderCatalog {
  return {
    providers: array(record.providers, "providers").map((value) => {
      const row = object(value, "provider");
      return {
        provider_id: text(row.provider_id, "provider_id"),
        admission_status: text(row.admission_status, "admission_status"),
        approved_resources: strings(row.approved_resources, "approved_resources"),
        d3_acquisition_resources: strings(row.d3_acquisition_resources, "d3_acquisition_resources"),
        internal_use_only: Boolean(row.internal_use_only),
        redistribution_enabled: Boolean(row.redistribution_enabled),
        credential_mode: text(row.credential_mode, "credential_mode"),
        credential_reference: nullableText(row.credential_reference),
        credential_state: text(row.credential_state, "credential_state"),
        credential_code: text(row.credential_code, "credential_code"),
        credential_remediation: nullableText(row.credential_remediation),
        network_required: Boolean(row.network_required),
        acquisition_available: Boolean(row.acquisition_available),
        available_actions: strings(row.available_actions, "available_actions"),
        evidence_reviewed_at: text(row.evidence_reviewed_at, "evidence_reviewed_at"),
        rationale: text(row.rationale, "rationale"),
        findings: strings(row.findings, "findings"),
        promotion_automatic: Boolean(row.promotion_automatic)
      };
    }),
    offline_paths: array(record.offline_paths, "offline_paths").map((value) => {
      const path = object(value, "offline path");
      return { id: text(path.id, "id"), label: text(path.label, "label"), network_required: Boolean(path.network_required), credential_required: Boolean(path.credential_required), available: Boolean(path.available) };
    }),
    network_consent_mode: text(record.network_consent_mode, "network_consent_mode"),
    provider_promotion_automatic: Boolean(record.provider_promotion_automatic),
    recommendations_enabled: Boolean(record.recommendations_enabled),
    live_execution_enabled: Boolean(record.live_execution_enabled)
  };
}

function parseCredential(record: Record<string, unknown>): CredentialResult {
  return {
    operation: text(record.operation, "operation"), provider_id: text(record.provider_id, "provider_id"), reference: text(record.reference, "reference"), state: text(record.state, "state"), code: text(record.code, "code"), remediation: nullableText(record.remediation), admission_status: text(record.admission_status, "admission_status"), acquisition_available: Boolean(record.acquisition_available), provider_promotion_automatic: Boolean(record.provider_promotion_automatic), secret_value_returned: false, ...(typeof record.deleted === "boolean" ? { deleted: record.deleted } : {})
  };
}

function parseEvidence(record: Record<string, unknown>): AcquisitionEvidence {
  return {
    acquisition_id: text(record.acquisition_id, "acquisition_id"), request_id: text(record.request_id, "request_id"), job_id: text(record.job_id, "job_id"), job_status: text(record.job_status, "job_status"), status: text(record.status, "status"), provider_id: text(record.provider_id, "provider_id"), symbol: text(record.symbol, "symbol"), timeframe: text(record.timeframe, "timeframe"), progress_percent: number(record.progress_percent, "progress_percent"), dataset_revision_id: nullableText(record.dataset_revision_id), canonical_row_count: nullableNumber(record.canonical_row_count), source_attribution: text(record.source_attribution, "source_attribution"), quota_state: text(record.quota_state, "quota_state"), retry_after_seconds: nullableNumber(record.retry_after_seconds), reuse_state: text(record.reuse_state, "reuse_state"), rationale: text(record.rationale, "rationale"), remediation: strings(record.remediation, "remediation"), findings: strings(record.findings, "findings"), recommendations_enabled: false, broker_execution_enabled: false, real_capital_execution_enabled: false
  };
}

function object(value: unknown, label: string): Record<string, unknown> { if (typeof value !== "object" || value === null || Array.isArray(value)) throw new DataSourcesClientError("invalid_response", `${label} must be an object.`, true); return value as Record<string, unknown>; }
function array(value: unknown, label: string): unknown[] { if (!Array.isArray(value)) throw new DataSourcesClientError("invalid_response", `${label} must be an array.`, true); return value; }
function text(value: unknown, label: string): string { if (typeof value !== "string") throw new DataSourcesClientError("invalid_response", `${label} must be a string.`, true); return value; }
function nullableText(value: unknown): string | null { return value === null || value === undefined ? null : text(value, "nullable string"); }
function number(value: unknown, label: string): number { if (typeof value !== "number" || !Number.isFinite(value)) throw new DataSourcesClientError("invalid_response", `${label} must be a finite number.`, true); return value; }
function nullableNumber(value: unknown): number | null { return value === null || value === undefined ? null : number(value, "nullable number"); }
function strings(value: unknown, label: string): string[] { return array(value, label).map((item) => text(item, label)); }
