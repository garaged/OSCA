import { useEffect, useRef, useState } from "react";
import { App } from "./App";
import { bootstrapDesktop, DesktopClientError } from "./api";
import { DataSourcesSurface } from "./DataSources";
import { DesktopAreaGuidance, menuHint } from "./DesktopGuidance";
import { MarketsSurface } from "./Markets";
import { PaperForwardLabSurface } from "./PaperForwardLab";
import { PortfolioAnalyticsSurface } from "./PortfolioAnalytics";
import { PortfolioLabSurface } from "./PortfolioLab";
import { PortfolioOperationsSurface } from "./PortfolioOperations";
import { ProjectsSurface } from "./Projects";
import { StrategyLabSurface } from "./StrategyLab";
import { WorkbenchSurface } from "./Workbench";
import "./d3Root.css";
import "./portfolioOperations.css";

type RootView =
  | "workspace"
  | "markets"
  | "workbench"
  | "projects"
  | "strategy-lab"
  | "portfolio-lab"
  | "paper-lab"
  | "data-sources";
type ProfileState =
  | { kind: "loading" }
  | { kind: "ready"; profileRoot?: string }
  | { kind: "error"; error: DesktopClientError };

const views: RootView[] = [
  "workspace",
  "markets",
  "workbench",
  "projects",
  "strategy-lab",
  "portfolio-lab",
  "paper-lab",
  "data-sources"
];

function viewLabel(view: RootView): string {
  if (view === "data-sources") return "Data Sources";
  if (view === "strategy-lab") return "Strategy Lab";
  if (view === "portfolio-lab") return "Portfolio Lab";
  if (view === "paper-lab") return "Paper Lab";
  return view[0].toUpperCase() + view.slice(1);
}

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
            <span className="d3-mode-label">{viewLabel(item)}</span>
            <span className="d3-mode-description">{menuHint(item)}</span>
          </button>
        ))}
      </nav>

      {view === "workspace" ? (
        <>
          <DesktopAreaGuidance view={view} />
          <App />
        </>
      ) : (
        <main className="d3-data-sources-main">
          <h1 className="visually-hidden" ref={headingRef} tabIndex={-1}>
            {viewLabel(view)}
          </h1>
          <DesktopAreaGuidance view={view} />
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
                    : view === "workbench"
                      ? "Open a validated profile from Workspace before loading governed analytical data in Workbench."
                      : view === "projects"
                        ? "Open a validated profile from Workspace before creating research projects."
                        : view === "strategy-lab"
                          ? "Open a validated profile from Workspace before using Strategy Lab."
                          : view === "portfolio-lab"
                            ? "Open a validated profile from Workspace before using Portfolio Lab."
                            : view === "paper-lab"
                              ? "Open and own a validated profile from Workspace before using simulated Paper Lab."
                              : "Provider policy and credential state remain inspectable, but import, acquisition, and retained evidence require a validated profile selected from Workspace."}
                </aside>
              ) : null}
              {view === "markets" ? (
                <MarketsSurface profileRoot={profile.profileRoot} />
              ) : view === "workbench" ? (
                <WorkbenchSurface profileRoot={profile.profileRoot} />
              ) : view === "projects" ? (
                <ProjectsSurface profileRoot={profile.profileRoot} />
              ) : view === "strategy-lab" ? (
                <StrategyLabSurface profileRoot={profile.profileRoot} />
              ) : view === "portfolio-lab" ? (
                <>
                  <PortfolioLabSurface profileRoot={profile.profileRoot} />
                  <PortfolioOperationsSurface profileRoot={profile.profileRoot} />
                  <PortfolioAnalyticsSurface profileRoot={profile.profileRoot} />
                </>
              ) : view === "paper-lab" ? (
                <PaperForwardLabSurface profileRoot={profile.profileRoot} />
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
