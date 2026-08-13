import { invoke } from "@tauri-apps/api/core";

export class ProjectClientError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly retryable = false
  ) {
    super(message);
    this.name = "ProjectClientError";
  }
}

export type ProjectSummary = {
  project_id: number;
  project_uuid: string;
  name: string;
  objective: string;
  horizon: string | null;
  status: string;
  cloned_from_uuid: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectPin = {
  pin_id: number;
  project_id: number;
  pin_type: string;
  source_id: string;
  label: string;
  metadata: Record<string, unknown>;
  degraded_status: string;
  created_at: string;
  updated_at: string;
};

export type ProjectNote = {
  note_id: number;
  project_id: number;
  title: string | null;
  body: string;
  user_authored: boolean;
  evidence_role: string;
  created_at: string;
  updated_at: string;
};

export type ProjectWorkspace = {
  workspace_id: number;
  project_id: number;
  name: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ProjectTimelineEvent = {
  event_id: number;
  project_id: number;
  event_type: string;
  details: Record<string, unknown>;
  created_at: string;
};

export type ResearchProject = ProjectSummary & {
  pins: ProjectPin[];
  notes: ProjectNote[];
  workspaces: ProjectWorkspace[];
  timeline: ProjectTimelineEvent[];
};

export type ProjectExport = {
  project_id: number;
  manifest_path: string;
  manifest_sha256: string;
  thin_manifest: boolean;
  self_contained_package: boolean;
};

export function listProjects(
  profileRoot: string,
  includeArchived = true,
  includeDeleted = false
): Promise<ProjectSummary[]> {
  return request("project.list", {
    profile_root: profileRoot,
    include_archived: includeArchived,
    include_deleted: includeDeleted
  }, (row) => array(row.projects, "projects").map((item) => parseProjectSummary(object(item, "project"))));
}

export function getProject(profileRoot: string, projectId: number): Promise<ResearchProject> {
  return request(
    "project.get",
    { profile_root: profileRoot, project_id: projectId },
    (row) => parseProject(object(row.project, "project"))
  );
}

export function createProject(
  profileRoot: string,
  name: string,
  objective: string,
  horizon: string | null
): Promise<ResearchProject> {
  return request(
    "project.create",
    { profile_root: profileRoot, name, objective, horizon },
    (row) => parseProject(object(row.project, "project"))
  );
}

export function updateProject(
  profileRoot: string,
  projectId: number,
  values: { horizon?: string | null; name?: string; objective?: string }
): Promise<ResearchProject> {
  return request(
    "project.update",
    { profile_root: profileRoot, project_id: projectId, ...values },
    (row) => parseProject(object(row.project, "project"))
  );
}

export function archiveProject(profileRoot: string, projectId: number): Promise<ResearchProject> {
  return projectTransition("project.archive", profileRoot, projectId);
}

export function restoreProject(profileRoot: string, projectId: number): Promise<ResearchProject> {
  return projectTransition("project.restore", profileRoot, projectId);
}

export function cloneProject(
  profileRoot: string,
  projectId: number,
  name: string
): Promise<ResearchProject> {
  return request(
    "project.clone",
    { profile_root: profileRoot, project_id: projectId, name },
    (row) => parseProject(object(row.project, "project"))
  );
}

export function addProjectPin(
  profileRoot: string,
  projectId: number,
  pinType: string,
  sourceId: string,
  label: string,
  metadata: Record<string, unknown> = {}
): Promise<ProjectPin> {
  return request(
    "project.pin.add",
    { profile_root: profileRoot, project_id: projectId, pin_type: pinType, source_id: sourceId, label, metadata },
    (row) => parsePin(object(row.pin, "pin"))
  );
}

export function addProjectNote(
  profileRoot: string,
  projectId: number,
  title: string | null,
  body: string
): Promise<ProjectNote> {
  return request(
    "project.note.add",
    { profile_root: profileRoot, project_id: projectId, title, body },
    (row) => parseNote(object(row.note, "note"))
  );
}

export function saveProjectWorkspace(
  profileRoot: string,
  projectId: number,
  name: string,
  config: Record<string, unknown>
): Promise<ProjectWorkspace> {
  return request(
    "project.workspace.save",
    { profile_root: profileRoot, project_id: projectId, name, config },
    (row) => parseWorkspace(object(row.workspace, "workspace"))
  );
}

export function prepareProjectExport(
  profileRoot: string,
  projectId: number
): Promise<ProjectExport> {
  return request(
    "project.export.prepare",
    { profile_root: profileRoot, project_id: projectId },
    (row) => ({
      project_id: number(row.project_id, "project_id"),
      manifest_path: text(row.manifest_path, "manifest_path"),
      manifest_sha256: text(row.manifest_sha256, "manifest_sha256"),
      thin_manifest: Boolean(row.thin_manifest),
      self_contained_package: Boolean(row.self_contained_package)
    })
  );
}

function projectTransition(
  method: string,
  profileRoot: string,
  projectId: number
): Promise<ResearchProject> {
  return request(
    method,
    { profile_root: profileRoot, project_id: projectId },
    (row) => parseProject(object(row.project, "project"))
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
    throw new ProjectClientError(
      "sidecar_unavailable",
      error instanceof Error ? error.message : "The OSCA sidecar is unavailable.",
      true
    );
  }
  const envelope = object(JSON.parse(raw) as unknown, "desktop response");
  if (text(envelope.request_id, "request_id") !== requestId) {
    throw new ProjectClientError(
      "invalid_response",
      "Desktop response identity did not match the request.",
      true
    );
  }
  if (text(envelope.status, "status") === "error") {
    const failure = object(envelope.error, "error");
    throw new ProjectClientError(
      text(failure.code, "error.code"),
      text(failure.message, "error.message"),
      Boolean(failure.retryable)
    );
  }
  return parse(object(envelope.result, "result"));
}

function parseProject(row: Record<string, unknown>): ResearchProject {
  return {
    ...parseProjectSummary(row),
    pins: array(row.pins, "pins").map((item) => parsePin(object(item, "pin"))),
    notes: array(row.notes, "notes").map((item) => parseNote(object(item, "note"))),
    workspaces: array(row.workspaces, "workspaces").map((item) => parseWorkspace(object(item, "workspace"))),
    timeline: array(row.timeline, "timeline").map((item) => parseTimelineEvent(object(item, "timeline event")))
  };
}

function parseProjectSummary(row: Record<string, unknown>): ProjectSummary {
  return {
    project_id: number(row.project_id, "project_id"),
    project_uuid: text(row.project_uuid, "project_uuid"),
    name: text(row.name, "name"),
    objective: text(row.objective, "objective"),
    horizon: row.horizon == null ? null : text(row.horizon, "horizon"),
    status: text(row.status, "status"),
    cloned_from_uuid: row.cloned_from_uuid == null ? null : text(row.cloned_from_uuid, "cloned_from_uuid"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function parsePin(row: Record<string, unknown>): ProjectPin {
  return {
    pin_id: number(row.pin_id, "pin_id"),
    project_id: number(row.project_id, "project_id"),
    pin_type: text(row.pin_type, "pin_type"),
    source_id: text(row.source_id, "source_id"),
    label: text(row.label, "label"),
    metadata: object(row.metadata, "metadata"),
    degraded_status: text(row.degraded_status, "degraded_status"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function parseNote(row: Record<string, unknown>): ProjectNote {
  return {
    note_id: number(row.note_id, "note_id"),
    project_id: number(row.project_id, "project_id"),
    title: row.title == null ? null : text(row.title, "title"),
    body: text(row.body, "body"),
    user_authored: Boolean(row.user_authored),
    evidence_role: text(row.evidence_role, "evidence_role"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function parseWorkspace(row: Record<string, unknown>): ProjectWorkspace {
  return {
    workspace_id: number(row.workspace_id, "workspace_id"),
    project_id: number(row.project_id, "project_id"),
    name: text(row.name, "name"),
    config: object(row.config, "config"),
    created_at: text(row.created_at, "created_at"),
    updated_at: text(row.updated_at, "updated_at")
  };
}

function parseTimelineEvent(row: Record<string, unknown>): ProjectTimelineEvent {
  return {
    event_id: number(row.event_id, "event_id"),
    project_id: number(row.project_id, "project_id"),
    event_type: text(row.event_type, "event_type"),
    details: object(row.details, "details"),
    created_at: text(row.created_at, "created_at")
  };
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new ProjectClientError("invalid_response", `${label} must be an object.`, true);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new ProjectClientError("invalid_response", `${label} must be an array.`, true);
  }
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new ProjectClientError("invalid_response", `${label} must be a string.`, true);
  }
  return value;
}

function number(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new ProjectClientError("invalid_response", `${label} must be a number.`, true);
  }
  return value;
}
