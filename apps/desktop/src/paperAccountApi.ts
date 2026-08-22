import { invoke } from "@tauri-apps/api/core";
import { DesktopClientError, DesktopErrorPayload } from "./api";

export type PaperAccount = {
  paper_account_id: string;
  name: string;
  base_currency: string;
  status: "active" | "paused" | "closed";
  created_at: string;
};

export type PaperControlDecision = {
  control_decision_id: string;
  paper_account_id: string;
  action: "allow" | "pause" | "kill_switch";
  can_process: boolean;
  reason: string;
  effective_at: string;
};

export type PaperAccountRecord = {
  account: PaperAccount;
  latest_control: PaperControlDecision | null;
};

type Envelope = {
  request_id: string;
  status: "ok" | "error";
  result: Record<string, unknown> | null;
  error: DesktopErrorPayload | null;
};

export async function listPaperAccounts(profileRoot: string): Promise<PaperAccountRecord[]> {
  return request(
    "paper.account.list",
    { profile_root: profileRoot },
    (record) => array(record.accounts, "accounts").map(parseAccountRecord)
  );
}

export async function createPaperAccount(
  profileRoot: string,
  name: string,
  baseCurrency: string
): Promise<PaperAccount> {
  return request(
    "paper.account.create",
    {
      profile_root: profileRoot,
      name,
      base_currency: baseCurrency,
      created_at: new Date().toISOString()
    },
    (record) => parseAccount(object(record.account, "account"))
  );
}

export async function recordPaperControl(
  profileRoot: string,
  paperAccountId: string,
  action: "allow" | "pause" | "kill_switch",
  reason: string
): Promise<PaperControlDecision> {
  return request(
    "paper.account.control.record",
    {
      profile_root: profileRoot,
      paper_account_id: paperAccountId,
      action,
      reason
    },
    (record) => parseControl(object(record.control_decision, "control_decision"))
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
  if (!envelope.result) throw invalid("Paper account response contained no result.");
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

function parseAccountRecord(value: unknown): PaperAccountRecord {
  const record = object(value, "paper account record");
  return {
    account: parseAccount(object(record.account, "account")),
    latest_control:
      record.latest_control == null
        ? null
        : parseControl(object(record.latest_control, "latest_control"))
  };
}

function parseAccount(record: Record<string, unknown>): PaperAccount {
  const status = string(record.status, "status");
  if (status !== "active" && status !== "paused" && status !== "closed") {
    throw invalid("Invalid paper account status.");
  }
  return {
    paper_account_id: string(record.paper_account_id, "paper_account_id"),
    name: string(record.name, "name"),
    base_currency: string(record.base_currency, "base_currency"),
    status,
    created_at: string(record.created_at, "created_at")
  };
}

function parseControl(record: Record<string, unknown>): PaperControlDecision {
  const action = string(record.action, "action");
  if (action !== "allow" && action !== "pause" && action !== "kill_switch") {
    throw invalid("Invalid paper control action.");
  }
  return {
    control_decision_id: string(record.control_decision_id, "control_decision_id"),
    paper_account_id: string(record.paper_account_id, "paper_account_id"),
    action,
    can_process: boolean(record.can_process, "can_process"),
    reason: string(record.reason, "reason"),
    effective_at: string(record.effective_at, "effective_at")
  };
}

function parseError(record: Record<string, unknown>): DesktopErrorPayload {
  return {
    code: string(record.code, "error.code"),
    message: string(record.message, "error.message"),
    retryable: record.retryable === true
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw invalid(`${label} must be an object.`);
  }
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

function boolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") throw invalid(`${label} must be boolean.`);
  return value;
}

function invalid(message: string): DesktopClientError {
  return new DesktopClientError({ code: "invalid_response", message, retryable: false });
}
