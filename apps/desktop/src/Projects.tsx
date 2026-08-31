import { FormEvent, useEffect, useState } from "react";
import {
  addProjectNote,
  addProjectPin,
  archiveProject,
  cloneProject,
  createProject,
  getProject,
  listProjects,
  prepareProjectExport,
  ProjectClientError,
  ProjectExport,
  ProjectSummary,
  ResearchProject,
  restoreProject,
  saveProjectWorkspace
} from "./projectApi";
import "./projects.css";

type ResultState<T> =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; value: T }
  | { kind: "error"; message: string };

export function ProjectsSurface({ profileRoot }: { profileRoot?: string }) {
  const [projects, setProjects] = useState<ResultState<ProjectSummary[]>>({ kind: "idle" });
  const [active, setActive] = useState<ResultState<ResearchProject>>({ kind: "idle" });
  const [notice, setNotice] = useState<string | null>(null);
  const [exportState, setExportState] = useState<ResultState<ProjectExport>>({ kind: "idle" });
  const [name, setName] = useState("");
  const [objective, setObjective] = useState("");
  const [horizon, setHorizon] = useState("");
  const [pinType, setPinType] = useState("asset");
  const [pinSource, setPinSource] = useState("");
  const [pinLabel, setPinLabel] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");

  async function reloadProjects(selectId?: number) {
    if (!profileRoot) {
      setProjects({ kind: "ready", value: [] });
      setActive({ kind: "idle" });
      return;
    }
    setProjects({ kind: "loading" });
    try {
      const rows = await listProjects(profileRoot);
      setProjects({ kind: "ready", value: rows });
      const nextId = selectId ?? rows[0]?.project_id;
      if (nextId) {
        await loadProject(nextId);
      } else {
        setActive({ kind: "idle" });
      }
    } catch (error) {
      setProjects({ kind: "error", message: message(error) });
    }
  }

  async function loadProject(projectId: number) {
    if (!profileRoot) return;
    setActive({ kind: "loading" });
    setExportState({ kind: "idle" });
    try {
      setActive({ kind: "ready", value: await getProject(profileRoot, projectId) });
    } catch (error) {
      setActive({ kind: "error", message: message(error) });
    }
  }

  useEffect(() => {
    void reloadProjects();
  }, [profileRoot]);

  async function submitProject(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot) return;
    try {
      const created = await createProject(profileRoot, name, objective, horizon || null);
      setName("");
      setObjective("");
      setHorizon("");
      setNotice("Project created.");
      await reloadProjects(created.project_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function archiveActive() {
    if (!profileRoot || active.kind !== "ready") return;
    try {
      const archived = await archiveProject(profileRoot, active.value.project_id);
      setActive({ kind: "ready", value: archived });
      setNotice("Project archived.");
      await reloadProjects(archived.project_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function restoreActive() {
    if (!profileRoot || active.kind !== "ready") return;
    try {
      const restored = await restoreProject(profileRoot, active.value.project_id);
      setActive({ kind: "ready", value: restored });
      setNotice("Project restored.");
      await reloadProjects(restored.project_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function cloneActive() {
    if (!profileRoot || active.kind !== "ready") return;
    try {
      const cloned = await cloneProject(profileRoot, active.value.project_id, `${active.value.name} clone`);
      setNotice("Project cloned.");
      await reloadProjects(cloned.project_id);
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitPin(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || active.kind !== "ready") return;
    try {
      await addProjectPin(profileRoot, active.value.project_id, pinType, pinSource, pinLabel || pinSource);
      setPinSource("");
      setPinLabel("");
      await loadProject(active.value.project_id);
      setNotice("Pin added.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function submitNote(event: FormEvent) {
    event.preventDefault();
    if (!profileRoot || active.kind !== "ready") return;
    try {
      await addProjectNote(profileRoot, active.value.project_id, noteTitle || null, noteBody);
      setNoteTitle("");
      setNoteBody("");
      await loadProject(active.value.project_id);
      setNotice("User note added.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function saveWorkspace() {
    if (!profileRoot || active.kind !== "ready") return;
    try {
      await saveProjectWorkspace(profileRoot, active.value.project_id, workspaceName || "Project overview", {
        selected_project_id: active.value.project_id,
        visible_sections: ["pins", "notes", "timeline"],
        selected_pin_ids: active.value.pins.map((pin) => pin.pin_id)
      });
      setWorkspaceName("");
      await loadProject(active.value.project_id);
      setNotice("Workspace saved.");
    } catch (error) {
      setNotice(message(error));
    }
  }

  async function exportManifest() {
    if (!profileRoot || active.kind !== "ready") return;
    setExportState({ kind: "loading" });
    try {
      setExportState({
        kind: "ready",
        value: await prepareProjectExport(profileRoot, active.value.project_id)
      });
      await loadProject(active.value.project_id);
    } catch (error) {
      setExportState({ kind: "error", message: message(error) });
    }
  }

  const activeProject = active.kind === "ready" ? active.value : null;

  return (
    <section className="projects" aria-labelledby="projects-heading">
      <header className="projects-hero">
        <div>
          <p className="eyebrow">D6 research projects</p>
          <h1 id="projects-heading">Projects</h1>
          <p>Organize objectives, governed evidence pins, user notes, saved workspaces, and reproducible manifest exports.</p>
        </div>
        <div className="projects-boundaries">
          <span>Typed pins</span>
          <span>User notes</span>
          <span>Research only</span>
        </div>
      </header>

      {notice ? <p className="projects-notice" role="status">{notice}</p> : null}
      {!profileRoot ? (
        <p className="projects-notice" role="note">Open a validated profile from Workspace before creating research projects.</p>
      ) : null}

      <div className="projects-layout">
        <section className="projects-panel" aria-labelledby="project-create-title">
          <h2 id="project-create-title">Create project</h2>
          <form className="projects-form" onSubmit={(event) => void submitProject(event)}>
            <label>Name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
            <label>Objective<textarea value={objective} onChange={(event) => setObjective(event.target.value)} /></label>
            <label>Horizon<input value={horizon} onChange={(event) => setHorizon(event.target.value)} /></label>
            <button disabled={!profileRoot} type="submit">Create project</button>
          </form>
        </section>

        <section className="projects-panel" aria-labelledby="project-list-title">
          <h2 id="project-list-title">Project list</h2>
          {projects.kind === "loading" ? <p role="status">Loading projects…</p> : null}
          {projects.kind === "error" ? <p role="alert">{projects.message}</p> : null}
          {projects.kind === "ready" && projects.value.length === 0 ? <p>No projects yet.</p> : null}
          <div className="project-list">
            {projects.kind === "ready" ? projects.value.map((project) => (
              <button
                aria-pressed={activeProject?.project_id === project.project_id}
                key={project.project_id}
                onClick={() => void loadProject(project.project_id)}
                type="button"
              >
                <strong>{project.name}</strong>
                <span>{project.status} · {project.objective}</span>
              </button>
            )) : null}
          </div>
        </section>
      </div>

      {active.kind === "loading" ? <p className="projects-notice" role="status">Loading project detail…</p> : null}
      {active.kind === "error" ? <p className="projects-notice" role="alert">{active.message}</p> : null}
      {activeProject ? (
        <ProjectDetail
          exportManifest={exportManifest}
          exportState={exportState}
          onArchive={archiveActive}
          onClone={cloneActive}
          onRestore={restoreActive}
          pinForm={{
            pinLabel,
            pinSource,
            pinType,
            setPinLabel,
            setPinSource,
            setPinType,
            submitPin
          }}
          noteForm={{
            noteBody,
            noteTitle,
            setNoteBody,
            setNoteTitle,
            submitNote
          }}
          project={activeProject}
          saveWorkspace={saveWorkspace}
          setWorkspaceName={setWorkspaceName}
          workspaceName={workspaceName}
        />
      ) : null}
    </section>
  );
}

function ProjectDetail({
  exportManifest,
  exportState,
  noteForm,
  onArchive,
  onClone,
  onRestore,
  pinForm,
  project,
  saveWorkspace,
  setWorkspaceName,
  workspaceName
}: {
  exportManifest: () => Promise<void>;
  exportState: ResultState<ProjectExport>;
  noteForm: {
    noteBody: string;
    noteTitle: string;
    setNoteBody: (value: string) => void;
    setNoteTitle: (value: string) => void;
    submitNote: (event: FormEvent) => void | Promise<void>;
  };
  onArchive: () => Promise<void>;
  onClone: () => Promise<void>;
  onRestore: () => Promise<void>;
  pinForm: {
    pinLabel: string;
    pinSource: string;
    pinType: string;
    setPinLabel: (value: string) => void;
    setPinSource: (value: string) => void;
    setPinType: (value: string) => void;
    submitPin: (event: FormEvent) => void | Promise<void>;
  };
  project: ResearchProject;
  saveWorkspace: () => Promise<void>;
  setWorkspaceName: (value: string) => void;
  workspaceName: string;
}) {
  return (
    <section className="project-detail" aria-labelledby="project-detail-title">
      <div className="project-detail-heading">
        <div>
          <p className="eyebrow">Selected project</p>
          <h2 id="project-detail-title">{project.name}</h2>
          <p>{project.objective}</p>
        </div>
        <div className="project-actions">
          <button onClick={() => void onClone()} type="button">Clone</button>
          {project.status === "archived" ? (
            <button onClick={() => void onRestore()} type="button">Restore</button>
          ) : (
            <button onClick={() => void onArchive()} type="button">Archive</button>
          )}
          <button onClick={() => void exportManifest()} type="button">Export manifest</button>
        </div>
      </div>

      <dl className="project-summary">
        <div><dt>Status</dt><dd>{project.status}</dd></div>
        <div><dt>Horizon</dt><dd>{project.horizon ?? "Not set"}</dd></div>
        <div><dt>Project UUID</dt><dd>{project.project_uuid}</dd></div>
        <div><dt>Clone source</dt><dd>{project.cloned_from_uuid ?? "Original project"}</dd></div>
      </dl>

      {exportState.kind === "loading" ? <p className="projects-notice" role="status">Preparing project manifest…</p> : null}
      {exportState.kind === "error" ? <p className="projects-notice" role="alert">{exportState.message}</p> : null}
      {exportState.kind === "ready" ? (
        <section className="projects-export" aria-labelledby="project-export-title">
          <h3 id="project-export-title">Manifest export prepared</h3>
          <p><strong>Manifest:</strong> {exportState.value.manifest_path}</p>
          <p><strong>SHA-256:</strong> {exportState.value.manifest_sha256}</p>
          <p>Thin manifest: {exportState.value.thin_manifest ? "yes" : "no"}. Self-contained package: {exportState.value.self_contained_package ? "yes" : "no"}.</p>
        </section>
      ) : null}

      <div className="project-grid">
        <section className="projects-panel" aria-labelledby="pins-title">
          <h3 id="pins-title">Evidence pins</h3>
          <form className="projects-form" onSubmit={(event) => pinForm.submitPin(event)}>
            <label>Type
              <select value={pinForm.pinType} onChange={(event) => pinForm.setPinType(event.target.value)}>
                <option value="asset">Asset</option>
                <option value="watchlist">Watchlist</option>
                <option value="dataset_revision">Dataset revision</option>
                <option value="workbench_view">Workbench view</option>
                <option value="workbench_export">Workbench export</option>
                <option value="strategy">Strategy</option>
                <option value="strategy_version">Strategy version</option>
                <option value="backtest_result">Backtest result</option>
                <option value="ml_experiment">ML experiment</option>
                <option value="report">Report</option>
                <option value="external_reference">External reference</option>
              </select>
            </label>
            <label>Source identity<input value={pinForm.pinSource} onChange={(event) => pinForm.setPinSource(event.target.value)} /></label>
            <label>Label<input value={pinForm.pinLabel} onChange={(event) => pinForm.setPinLabel(event.target.value)} /></label>
            <button type="submit">Add pin</button>
          </form>
          <ul className="project-items">
            {project.pins.map((pin) => (
              <li key={pin.pin_id}>
                <strong>{pin.label}</strong>
                <span>{pin.pin_type} · {pin.degraded_status}</span>
                <code>{pin.source_id}</code>
              </li>
            ))}
          </ul>
        </section>

        <section className="projects-panel" aria-labelledby="notes-title">
          <h3 id="notes-title">User notes</h3>
          <form className="projects-form" onSubmit={(event) => noteForm.submitNote(event)}>
            <label>Title<input value={noteForm.noteTitle} onChange={(event) => noteForm.setNoteTitle(event.target.value)} /></label>
            <label>Note<textarea value={noteForm.noteBody} onChange={(event) => noteForm.setNoteBody(event.target.value)} /></label>
            <button type="submit">Add user note</button>
          </form>
          <ul className="project-items">
            {project.notes.map((note) => (
              <li key={note.note_id}>
                <strong>{note.title ?? "Untitled note"}</strong>
                <span>{note.evidence_role} · user-authored {note.user_authored ? "yes" : "no"}</span>
                <p>{note.body}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="projects-panel" aria-labelledby="workspaces-title">
          <h3 id="workspaces-title">Saved workspaces</h3>
          <div className="projects-inline-action">
            <label>Workspace name<input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} /></label>
            <button onClick={() => void saveWorkspace()} type="button">Save workspace</button>
          </div>
          <ul className="project-items">
            {project.workspaces.map((workspace) => (
              <li key={workspace.workspace_id}>
                <strong>{workspace.name}</strong>
                <span>Declarative context only</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="projects-panel" aria-labelledby="timeline-title">
          <h3 id="timeline-title">Timeline</h3>
          <ol className="project-items">
            {project.timeline.map((event) => (
              <li key={event.event_id}>
                <strong>{event.event_type}</strong>
                <span>{event.created_at}</span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </section>
  );
}

function message(error: unknown): string {
  if (error instanceof ProjectClientError) {
    return error.message;
  }
  return error instanceof Error ? error.message : "Projects operation failed.";
}
