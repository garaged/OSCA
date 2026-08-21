export type PortfolioWorkspaceEventKind = "selection" | "mutation";
export type PortfolioWorkspaceSource = "lab" | "operations" | "analytics";

export type PortfolioWorkspaceEventDetail = {
  kind: PortfolioWorkspaceEventKind;
  portfolioId?: string;
  source: PortfolioWorkspaceSource;
};

const PORTFOLIO_WORKSPACE_EVENT = "osca:portfolio-workspace-change";

export function announcePortfolioWorkspaceChange(detail: PortfolioWorkspaceEventDetail): void {
  window.dispatchEvent(
    new CustomEvent<PortfolioWorkspaceEventDetail>(PORTFOLIO_WORKSPACE_EVENT, { detail })
  );
}

export function subscribePortfolioWorkspaceChanges(
  source: PortfolioWorkspaceSource,
  listener: (detail: PortfolioWorkspaceEventDetail) => void
): () => void {
  const handler = (event: Event) => {
    const detail = (event as CustomEvent<PortfolioWorkspaceEventDetail>).detail;
    if (!detail || detail.source === source) return;
    listener(detail);
  };

  window.addEventListener(PORTFOLIO_WORKSPACE_EVENT, handler);
  return () => window.removeEventListener(PORTFOLIO_WORKSPACE_EVENT, handler);
}
