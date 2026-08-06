import { useEffect, useRef, useState } from "react";
import { App } from "./App";
import { bootstrapDesktop, DesktopClientError } from "./api";
import { DataSourcesSurface } from "./DataSources";
import "./d3Root.css";

type RootView = "workspace" | "data-sources";
type ProfileState =
  | { kind: "loading" }
  | { kind: "ready"; profileRoot?: string }
  | { kind: "error"; error: DesktopClientError };

export function D3Root() {
  const [view, setView] = useState<RootView>("workspace");
  const [profile, setProfile] = useState<ProfileState>({ kind: "loading" });
  const headingRef = useRef<HTMLHeadingElement>(null);

  async function loadProfileContext() {
    setProfile({ kind: "loading" });
    try {
      const bootstrap = await bootstrapDesktop();
      setProfile({
        kind: "ready",
        ...(bootstrap.selected_profile ? { profileRoot: bootstrap.selected_profile } : {})
      });
    } catch (error) {
      setProfile({
        kind: "error",
        error:
          error instanceof DesktopClientError
            ? error
            : new DesktopClientError({
                code: "desktop_unavailable",
                message: error instanceof Error ? error.message : "Desktop service unavailable.",
                retryable: true
              })
      });
    }
  }

  useEffect(() => {
    void loadProfileContext();
  }, []);

  useEffect(() => {
    headingRef.current?.focus();
    if (view === "data-sources") {
      void loadProfileContext();
    }
  }, [view]);

  return (
    <div className="d3-root">
      <nav className="d3-mode-navigation" aria-label="Desktop areas">
        <button
          aria-current={view === "workspace" ? "page" : undefined}
          className="d3-mode-button"
          data-active={view === "workspace"}
          onClick={() => setView("workspace")}
          type="button"
        >
          Workspace
        </button>
        <button
          aria-current={view === "data-sources" ? "page" : undefined}
          className="d3-mode-button"
          data-active={view === "data-sources"}
          onClick={() => setView("data-sources")}
          type="button"
        >
          Data Sources
        </button>
      </nav>

      {view === "workspace" ? (
        <App />
      ) : (
        <main className="d3-data-sources-main" id="d3-data-sources-main">
          <h1 className="visually-hidden" ref={headingRef} tabIndex={-1}>
            Data Sources
          </h1>
          {profile.kind === "loading" ? (
            <p className="d3-context-state" role="status">
              Loading the selected profile context…
            </p>
          ) : profile.kind === "error" ? (
            <section className="d3-context-state" role="alert">
              <h2>Profile context unavailable</h2>
              <p>{profile.error.message}</p>
              {profile.error.retryable ? (
                <button onClick={() => void loadProfileContext()} type="button">
                  Retry
                </button>
              ) : null}
            </section>
          ) : (
            <>
              {!profile.profileRoot ? (
                <aside className="d3-context-state" role="note">
                  <strong>No profile selected.</strong> Provider policy and credential state remain
                  inspectable, but import, acquisition, and retained evidence require a validated
                  profile selected from Workspace.
                </aside>
              ) : null}
              <DataSourcesSurface profileRoot={profile.profileRoot} />
            </>
          )}
        </main>
      )}
    </div>
  );
}
