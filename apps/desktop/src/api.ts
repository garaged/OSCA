import { invoke } from "@tauri-apps/api/core";

export type DesktopErrorPayload = {
  code: string;
  message: string;
  retryable: boolean;
};

export class DesktopClientError extends Error {
  readonly code: string;
  readonly retryable: boolean;

  constructor(payload: DesktopErrorPayload) {
    super(payload.message);
    this.name = "DesktopClientError";
    this.code = payload.code;
    this.retryable = payload.retryable;
  }
}

export type NavigationItem = {
  id: "home" | "research" | "evidence" | "system";
  label: string;
  available: boolean;
  reason?: string;
};

export type DesktopProfileReference = {
  path: string;
  label: string;
  last_opened_at: string | null;
};

export type DesktopDisclosures = {
  research_only: string;
  local_storage: string;
  optional_network: string;
  providers: string;
  credentials: string;
  recommendations: string;
  live_execution: string;
};

export type DesktopBootstrap = {
  first_run_required: boolean;
  selected_profile: string | null;
  profiles: DesktopProfileReference[];
  navigation: NavigationItem[];
  disclosures: DesktopDisclosures;
  capabilities: Record<string, boolean>;
};

export type ProfileFinding = {
  check_id: string;
  status: string;
  message: string;
  remediation: string | null;
};

export type ProfileInspection = {
  profile_root: string;
  exists: boolean;
  configured: boolean;
  writable: boolean;
  lock_state: "available" | "locked" | "unavailable";
  compatibility_status: string;
  storage_root: string | null;
  can_open: boolean;
  findings: ProfileFinding[];
};

export type ProfileOperation = {
  status: string;
  selected_profile: string;
  profile: ProfileInspection;
  diagnostics?: Record<string, unknown>;
};

export type DesktopDiagnostics = {
  package: Record<string, unknown>;
  protocol_version: string;
  sidecar_status: string;
  network_policy: string;
  provider_status: string;
  recommendations_enabled: boolean;
  live_execution_enabled: boolean;
  profile: ProfileInspection | null;
  profile_diagnostics: Record<string, unknown> | null;
};

export type SampleImportResult = {
  status: string;
  sample_id: string;
  sample_label: string;
  synthetic: boolean;
  network_access_enabled: boolean;
  provider_account_required: boolean;
  credential_required: boolean;
  import: {
    dataset_revision_id: string;
    symbol: string;
    timeframe: string;
    row_count: number;
    payload_uri: string;
    metadata_uri: string;
    network_access_enabled: boolean;
  };
};

type DesktopEnvelope = {
  protocol_version: "1.0";
  request_id: string;
  status: "ok" | "error";
  result: Record<string, unknown> | null;
  error: DesktopErrorPayload | null;
};

export async function bootstrapDesktop(): Promise<DesktopBootstrap> {
  return requestResult("desktop.bootstrap", {}, parseBootstrap);
}

export async function inspectDesktopProfile(profileRoot: string): Promise<ProfileInspection> {
  return requestResult("profile.inspect", { profile_root: profileRoot }, parseProfileInspection);
}

export async function createDesktopProfile(profileRoot: string): Promise<ProfileOperation> {
  return requestResult("profile.create", { profile_root: profileRoot }, parseProfileOperation);
}

export async function selectDesktopProfile(profileRoot: string): Promise<ProfileOperation> {
  return requestResult("profile.select", { profile_root: profileRoot }, parseProfileOperation);
}

export async function openDesktopProfile(profileRoot: string): Promise<ProfileOperation> {
  return requestResult("profile.open", { profile_root: profileRoot }, parseProfileOperation);
}

export async function fetchDesktopDiagnostics(
  profileRoot?: string
): Promise<DesktopDiagnostics> {
  const params = profileRoot ? { profile_root: profileRoot } : {};
  return requestResult("system.diagnostics", params, parseDiagnostics);
}

export async function importBundledSample(profileRoot: string): Promise<SampleImportResult> {
  return requestResult("sample.import", { profile_root: profileRoot }, parseSampleImport);
}

function classifyInvokeFailure(error: unknown): DesktopErrorPayload {
  const message = error instanceof Error
    ? error.message
    : typeof error === "string"
      ? error
      : "The OSCA sidecar is unavailable.";

  if (
    message.includes("profile is already open in another OSCA window or process") ||
    message.includes("profile mutation requires this OSCA window to open and own the profile first")
  ) {
    return {
      code: "profile_locked",
      message,
      retryable: true
    };
  }

  return {
    code: "sidecar_unavailable",
    message,
    retryable: true
  };
}

async function requestResult<T>(
  method: string,
  params: Record<string, unknown>,
  parse: (record: Record<string, unknown>) => T
): Promise<T> {
  const requestId = crypto.randomUUID();
  const request = {
    protocol_version: "1.0",
    request_id: requestId,
    method,
    params
  };

  let raw: string;
  try {
    raw = await invoke<string>("desktop_request", {
      requestJson: JSON.stringify(request)
    });
  } catch (error) {
    throw new DesktopClientError(classifyInvokeFailure(error));
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new DesktopClientError({
      code: "invalid_response",
      message: "The OSCA sidecar returned invalid JSON.",
      retryable: true
    });
  }

  const envelope = parseEnvelope(parsed, requestId);
  if (envelope.status === "error") {
    throw new DesktopClientError(
      envelope.error ?? {
        code: "unknown_error",
        message: "The OSCA sidecar reported an unknown error.",
        retryable: false
      }
    );
  }
  if (envelope.result === null) {
    throw invalidResponse("The OSCA sidecar returned no result.");
  }
  return parse(envelope.result);
}

function parseEnvelope(value: unknown, requestId: string): DesktopEnvelope {
  const record = expectRecord(value, "desktop response");
  const protocolVersion = expectString(record.protocol_version, "protocol_version");
  if (protocolVersion !== "1.0") {
    throw invalidResponse(`Unsupported desktop protocol: ${protocolVersion}`);
  }
  const responseRequestId = expectString(record.request_id, "request_id");
  if (responseRequestId !== requestId) {
    throw invalidResponse("Desktop response request identity did not match the request.");
  }
  const status = expectString(record.status, "status");
  if (status !== "ok" && status !== "error") {
    throw invalidResponse("Desktop response status was not recognized.");
  }

  const result = record.result === null || record.result === undefined
    ? null
    : expectRecord(record.result, "result");
  const error = record.error === null || record.error === undefined
    ? null
    : parseError(expectRecord(record.error, "error"));

  return {
    protocol_version: "1.0",
    request_id: responseRequestId,
    status,
    result,
    error
  };
}

function parseBootstrap(record: Record<string, unknown>): DesktopBootstrap {
  const profiles = expectArray(record.profiles, "profiles").map((entry) => {
    const profile = expectRecord(entry, "profile");
    return {
      path: expectString(profile.path, "profile.path"),
      label: expectString(profile.label, "profile.label"),
      last_opened_at: expectNullableString(profile.last_opened_at, "profile.last_opened_at")
    };
  });
  const navigation = expectArray(record.navigation, "navigation").map((entry) => {
    const item = expectRecord(entry, "navigation item");
    const id = expectString(item.id, "navigation.id");
    if (!isNavigationId(id)) {
      throw invalidResponse(`Unknown navigation destination: ${id}`);
    }
    const reason = item.reason === undefined
      ? undefined
      : expectString(item.reason, "navigation.reason");
    return {
      id,
      label: expectString(item.label, "navigation.label"),
      available: expectBoolean(item.available, "navigation.available"),
      ...(reason ? { reason } : {})
    };
  });
  const disclosures = expectRecord(record.disclosures, "disclosures");
  const capabilities = expectRecord(record.capabilities, "capabilities");

  return {
    first_run_required: expectBoolean(record.first_run_required, "first_run_required"),
    selected_profile: expectNullableString(record.selected_profile, "selected_profile"),
    profiles,
    navigation,
    disclosures: {
      research_only: expectString(disclosures.research_only, "disclosures.research_only"),
      local_storage: expectString(disclosures.local_storage, "disclosures.local_storage"),
      optional_network: expectString(disclosures.optional_network, "disclosures.optional_network"),
      providers: expectString(disclosures.providers, "disclosures.providers"),
      credentials: expectString(disclosures.credentials, "disclosures.credentials"),
      recommendations: expectString(disclosures.recommendations, "disclosures.recommendations"),
      live_execution: expectString(disclosures.live_execution, "disclosures.live_execution")
    },
    capabilities: Object.fromEntries(
      Object.entries(capabilities).map(([key, value]) => [key, expectBoolean(value, `capabilities.${key}`)])
    )
  };
}

function parseProfileInspection(record: Record<string, unknown>): ProfileInspection {
  const lockState = expectString(record.lock_state, "profile.lock_state");
  if (lockState !== "available" && lockState !== "locked" && lockState !== "unavailable") {
    throw invalidResponse(`Unknown profile lock state: ${lockState}`);
  }
  return {
    profile_root: expectString(record.profile_root, "profile.profile_root"),
    exists: expectBoolean(record.exists, "profile.exists"),
    configured: expectBoolean(record.configured, "profile.configured"),
    writable: expectBoolean(record.writable, "profile.writable"),
    lock_state: lockState,
    compatibility_status: expectString(record.compatibility_status, "profile.compatibility_status"),
    storage_root: expectNullableString(record.storage_root, "profile.storage_root"),
    can_open: expectBoolean(record.can_open, "profile.can_open"),
    findings: expectArray(record.findings, "profile.findings").map((entry) => {
      const finding = expectRecord(entry, "profile finding");
      return {
        check_id: expectString(finding.check_id, "profile finding.check_id"),
        status: expectString(finding.status, "profile finding.status"),
        message: expectString(finding.message, "profile finding.message"),
        remediation: expectNullableString(finding.remediation, "profile finding.remediation")
      };
    })
  };
}

function parseProfileOperation(record: Record<string, unknown>): ProfileOperation {
  return {
    status: expectString(record.status, "profile operation.status"),
    selected_profile: expectString(record.selected_profile, "profile operation.selected_profile"),
    profile: parseProfileInspection(expectRecord(record.profile, "profile operation.profile")),
    ...(record.diagnostics === undefined || record.diagnostics === null
      ? {}
      : { diagnostics: expectRecord(record.diagnostics, "profile operation.diagnostics") })
  };
}

function parseDiagnostics(record: Record<string, unknown>): DesktopDiagnostics {
  return {
    package: expectRecord(record.package, "diagnostics.package"),
    protocol_version: expectString(record.protocol_version, "diagnostics.protocol_version"),
    sidecar_status: expectString(record.sidecar_status, "diagnostics.sidecar_status"),
    network_policy: expectString(record.network_policy, "diagnostics.network_policy"),
    provider_status: expectString(record.provider_status, "diagnostics.provider_status"),
    recommendations_enabled: expectBoolean(
      record.recommendations_enabled,
      "diagnostics.recommendations_enabled"
    ),
    live_execution_enabled: expectBoolean(record.live_execution_enabled, "diagnostics.live_execution_enabled"),
    profile: record.profile === null || record.profile === undefined
      ? null
      : parseProfileInspection(expectRecord(record.profile, "diagnostics.profile")),
    profile_diagnostics: record.profile_diagnostics === null || record.profile_diagnostics === undefined
      ? null
      : expectRecord(record.profile_diagnostics, "diagnostics.profile_diagnostics")
  };
}

function parseSampleImport(record: Record<string, unknown>): SampleImportResult {
  const imported = expectRecord(record.import, "sample import.import");
  return {
    status: expectString(record.status, "sample import.status"),
    sample_id: expectString(record.sample_id, "sample import.sample_id"),
    sample_label: expectString(record.sample_label, "sample import.sample_label"),
    synthetic: expectBoolean(record.synthetic, "sample import.synthetic"),
    network_access_enabled: expectBoolean(
      record.network_access_enabled,
      "sample import.network_access_enabled"
    ),
    provider_account_required: expectBoolean(
      record.provider_account_required,
      "sample import.provider_account_required"
    ),
    credential_required: expectBoolean(record.credential_required, "sample import.credential_required"),
    import: {
      dataset_revision_id: expectString(imported.dataset_revision_id, "sample import.dataset_revision_id"),
      symbol: expectString(imported.symbol, "sample import.symbol"),
      timeframe: expectString(imported.timeframe, "sample import.timeframe"),
      row_count: expectNumber(imported.row_count, "sample import.row_count"),
      payload_uri: expectString(imported.payload_uri, "sample import.payload_uri"),
      metadata_uri: expectString(imported.metadata_uri, "sample import.metadata_uri"),
      network_access_enabled: expectBoolean(
        imported.network_access_enabled,
        "sample import.import.network_access_enabled"
      )
    }
  };
}

function parseError(record: Record<string, unknown>): DesktopErrorPayload {
  return {
    code: expectString(record.code, "error.code"),
    message: expectString(record.message, "error.message"),
    retryable: expectBoolean(record.retryable, "error.retryable")
  };
}

function invalidResponse(message: string): DesktopClientError {
  return new DesktopClientError({
    code: "invalid_response",
    message,
    retryable: true
  });
}

function expectRecord(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw invalidResponse(`${label} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function expectArray(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw invalidResponse(`${label} must be an array.`);
  }
  return value;
}

function expectString(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw invalidResponse(`${label} must be a string.`);
  }
  return value;
}

function expectNullableString(value: unknown, label: string): string | null {
  if (value === null) {
    return null;
  }
  return expectString(value, label);
}

function expectBoolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    throw invalidResponse(`${label} must be a boolean.`);
  }
  return value;
}

function expectNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw invalidResponse(`${label} must be a number.`);
  }
  return value;
}

function isNavigationId(value: string): value is NavigationItem["id"] {
  return value === "home" || value === "research" || value === "evidence" || value === "system";
}
