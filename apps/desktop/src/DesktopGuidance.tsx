type RootView =
  | "workspace"
  | "markets"
  | "workbench"
  | "projects"
  | "strategy-lab"
  | "portfolio-lab"
  | "paper-lab"
  | "data-sources";

type Guidance = {
  short: string;
  purpose: string;
  steps: string[];
  note?: string;
};

const guidance: Record<RootView, Guidance> = {
  workspace: {
    short: "Profiles and app health",
    purpose: "Choose and own the local profile that contains your OSCA research state.",
    steps: [
      "Create or open a validated profile.",
      "Check diagnostics when another area says data or profile context is unavailable.",
      "Return here when you need to change profiles or release ownership."
    ]
  },
  markets: {
    short: "Find assets to research",
    purpose: "Discover stocks or crypto assets and keep a shortlist of what you want to study.",
    steps: [
      "Search for the asset you care about.",
      "Add useful assets to a watchlist or recent-assets context.",
      "Move to Workbench when you want to inspect actual governed price evidence."
    ]
  },
  workbench: {
    short: "Inspect charts and data",
    purpose: "Explore governed market series, ranges, tables, comparisons, and provenance before drawing conclusions.",
    steps: [
      "Select an asset and governed series.",
      "Inspect chart and table views together, including range and provenance.",
      "Use Strategy Lab only after the evidence window and assumptions make sense."
    ]
  },
  projects: {
    short: "Organize research evidence",
    purpose: "Keep related assets, strategy results, charts, and other evidence together as one research project.",
    steps: [
      "Create or open a project for a research question.",
      "Pin the evidence you want to preserve or revisit.",
      "Treat projects as organization, not as a source of new market calculations."
    ]
  },
  "strategy-lab": {
    short: "Test strategies historically",
    purpose: "Define transparent research rules, backtest them, and challenge them with sensitivity and walk-forward evaluation.",
    steps: [
      "Create or select a strategy and validate its rules.",
      "Run a historical backtest and inspect assumptions, costs, drawdown, and evidence range.",
      "Run sensitivity and walk-forward checks before trusting a good-looking result.",
      "Use Portfolio Lab or Paper Lab only after you understand the historical evidence."
    ],
    note: "A strong backtest is evidence about the past, not proof that the strategy will work in the future."
  },
  "portfolio-lab": {
    short: "Model virtual holdings",
    purpose: "Track simulated cash, positions, lots, valuation, P&L, and accounting evidence without real money.",
    steps: [
      "Create or select a virtual portfolio and starting cash.",
      "Record simulated acquisitions or other accounting operations.",
      "Retain valuation evidence so unrealized P&L and equity can be calculated.",
      "Use Paper Lab when you want future simulated orders to post into this portfolio automatically."
    ],
    note: "Portfolio Lab is an accounting model. It does not send orders to a broker or exchange."
  },
  "paper-lab": {
    short: "Simulate future orders",
    purpose: "Evaluate how explicit simulated orders would behave on later governed bars using retained execution assumptions.",
    steps: [
      "Select a D8 virtual portfolio and a retained paper account, then retain Allow simulation.",
      "Retain the paper run and execution assumptions first.",
      "Create and retain an immutable simulated-order draft.",
      "Confirm the draft separately, then process eligible governed bars and inspect fills/accounting.",
      "Use pause or the simulated kill switch whenever you want the local simulation to stop."
    ],
    note: "If Retain draft is disabled, first complete Retain run + assumptions. Paper Lab is simulated only and has no live-order path."
  },
  "data-sources": {
    short: "Import and govern data",
    purpose: "See where research data comes from, what providers are allowed, and how local/provider evidence enters OSCA.",
    steps: [
      "Check provider and policy state when data is unavailable elsewhere.",
      "Import governed CSV/Parquet evidence or use an explicitly admitted provider path.",
      "Verify source, revision, and quality state before using the data in Workbench or Strategy Lab."
    ]
  }
};

export function menuHint(view: RootView): string {
  return guidance[view].short;
}

export function DesktopAreaGuidance({ view }: { view: RootView }) {
  const item = guidance[view];
  return (
    <section className="desktop-area-guidance" aria-label={`${view} guidance`}>
      <p className="desktop-area-purpose">{item.purpose}</p>
      <details className="desktop-area-help">
        <summary>What do I do here?</summary>
        <ol>
          {item.steps.map((step) => <li key={step}>{step}</li>)}
        </ol>
        {item.note ? <p className="desktop-area-note">{item.note}</p> : null}
      </details>
    </section>
  );
}
