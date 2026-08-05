import { invoke } from "@tauri-apps/api/core";

export type DesktopResponse = {
  protocol_version: "1.0";
  request_id: string;
  status: "ok" | "error";
  result?: Record<string, unknown> | null;
  error?: { code: string; message: string; retryable: boolean } | null;
};

export async function requestDesktop(
  method: string,
  params: Record<string, unknown> = {}
): Promise<DesktopResponse> {
  const request = {
    protocol_version: "1.0",
    request_id: crypto.randomUUID(),
    method,
    params
  };
  const raw = await invoke<string>("desktop_request", {
    requestJson: JSON.stringify(request)
  });
  return JSON.parse(raw) as DesktopResponse;
}
