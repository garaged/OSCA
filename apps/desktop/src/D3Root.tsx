import { useEffect, useRef, useState } from "react";
import { App } from "./App";
import { bootstrapDesktop, DesktopClientError } from "./api";
import { DataSourcesSurface } from "./DataSources";
import { MarketsSurface } from "./Markets";
import "./d3Root.css";

type RootView = "workspace" | "markets" | "data-sources";
type ProfileState =
  | { kind: "loading" }
  | { kind: "ready"; profileRoot?: string }
  | { kind: "error"; error: DesktopClientError };

const views: RootView[] = ["workspace", "markets", "data-sources"];

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
        ...(bootstrap.selected_profile
          ? { profileRoot: bootstrap.selected_profile }
          : {})
      });
    } catch (error) {
      setProfile({
        kind: "error",
        error:
          error instanceof DesktopClientError
            ? error
            : new DesktopClientError({
                code: "desktop_unavailable",
                message:
                  error instanceof Error
                    ? error.message
                    : "Desktop service unavailable.",
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
    if (view !== "workspace") {
      void loadProfileContext();
    }
  }, [view]);

  return (
    <div className="d3-root">
      <nav className="d3-mode-navigation" aria-label="Desktop areas">
        {views.map((item) => (
          <button
            key={item}
            aria-current={view === item ? "page" : undefined}
            className="d3-mode-button"
            data-active={view === item}
            onClick={() => setView(item)}
            type="button"
          >
            {item === "data-sources"
              ? "Data Sources"
              : item[0].toUpperCase() + item.slice(1)}
          </button>
        ))}
      </nav>

      {view === "workspace" ? (
        <App />
      ) : (
        <main className="d3-data-sources-main">
          <h1 className="visually-hidden" ref={headingRef} tabIndex={-1}>
            {view === "markets" ? "Markets" : "Data Sources"}
          </h1>
          {profile.kind === "loading" ? (
            <p className="d3-context-state" role="status">
              Loading the selected profile context…
            </p>
          ) : profile.kind === "error" ? (
            <section className="d3-context-state" role="alert">
              <h2>Profile context unavailable</h2>
              <p>{profile.error.message}</p>
              <button onClick={() => void loadProfileContext()} type="button">
                Retry
              </button>
            </section>
          ) : (
            <>
              {!profile.profileRoot ? (
                <aside className="d3-context-state" role="note">
                  <strong>No profile selected.</strong>{" "}
                  {view === "markets"
                    ? "Asset search remains available, but persistent watchlists and recent assets require a validated profile selected from Workspace."
                    : "Provider policy and credential state remain inspectable, but import, acquisition, and retained evidence require a validated profile selected from Workspace."}
                </aside>
              ) : null}
              {view === "markets" ? (
                <MarketsSurface profileRoot={profile.profileRoot} />
              ) : (
                <DataSourcesSurface profileRoot={profile.profileRoot} />
              )}
            </>
          )}
        </main>
      )}
    </div>
  );
}
