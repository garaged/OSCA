import { FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import {
  bootstrapDesktop,
  createDesktopProfile,
  DesktopBootstrap,
  DesktopClientError,
  DesktopDiagnostics,
  DesktopDisclosures,
  DesktopProfileReference,
  fetchDesktopDiagnostics,
  importBundledSample,
  inspectDesktopProfile,
  NavigationItem,
  openDesktopProfile,
  ProfileInspection,
  SampleImportResult,
  selectDesktopProfile
} from "./api";

type ViewId = "home" | "system";

type AsyncState<T> =
  | { kind: "loading" }
  | { kind: "ready"; value: T }
  | { kind: "error"; error: DesktopClientError };

type ActionState =
  | { kind: "idle" }
  | { kind: "loading"; message: string }
  | { kind: "success"; message: string }
  | { kind: "error"; error: DesktopClientError };

const FALLBACK_NAVIGATION: NavigationItem[] = [
  { id: "home", label: "Home", available: true },
  {
    id: "research",
    label: "Research",
    available: false,
    reason: "Research workbench arrives in a later desktop milestone."
  },
  {
    id: "evidence",
    label: "Evidence",
    available: false,
    reason: "Desktop evidence navigation arrives after the shell foundation."
  },
  { id: "system", label: "System", available: true }
];

const FALLBACK_DISCLOSURES: DesktopDisclosures = {
  research_only: "OSCA is research and simulation software, not financial advice.",
  local_storage: "Profiles and imported data are stored locally on this machine.",
  optional_network: "Network access is optional and must be enabled explicitly.",
  providers: "No provider account is required for the bundled synthetic sample.",
  credentials: "This foundation does not request or expose provider credentials.",
  recommendations: "Recommendation generation is unavailable in D2.",
  live_execution: "Broker, exchange, autonomous, and real-capital execution are disabled."
};

export function App() {
  const [bootstrap, setBootstrap] = useState<AsyncState<DesktopBootstrap>>({ kind: "loading" });
  const [view, setView] = useState<ViewId>("home");
  const [profilePath, setProfilePath] = useState("");
  const [inspection, setInspection] = useState<ProfileInspection | null>(null);
  const [openedProfile, setOpenedProfile] = useState<ProfileInspection | null>(null);
  const [action, setAction] = useState<ActionState>({ kind: "idle" });
  const [sample, setSample] = useState<SampleImportResult | null>(null);
  const [diagnostics, setDiagnostics] = useState<AsyncState<DesktopDiagnostics>>({
    kind: "loading"
  });
  const mainHeadingRef = useRef<HTMLHeadingElement>(null);
  const actionErrorRef = useRef<HTMLDivElement>(null);

  async function loadBootstrap(preservePath = false) {
    setBootstrap({ kind: "loading" });
    try {
      const value = await bootstrapDesktop();
      setBootstrap({ kind: "ready", value });
      if (!preservePath) {
        setProfilePath(value.selected_profile ?? value.profiles[0]?.path ?? "");
      }
    } catch (error) {
      setBootstrap({ kind: "error", error: asDesktopError(error) });
    }
  }

  useEffect(() => {
    void loadBootstrap();
  }, []);

  useEffect(() => {
    mainHeadingRef.current?.focus();
  }, [view]);

  useEffect(() => {
    if (action.kind === "error") {
      actionErrorRef.current?.focus();
    }
  }, [action]);

  const bootstrapValue = bootstrap.kind === "ready" ? bootstrap.value : null;
  const navigation = bootstrapValue?.navigation ?? FALLBACK_NAVIGATION;
  const disclosures = bootstrapValue?.disclosures ?? FALLBACK_DISCLOSURES;
  const selectedProfile = bootstrapValue?.selected_profile ?? null;
  const activeProfilePath = openedProfile?.profile_root ?? selectedProfile ?? undefined;

  useEffect(() => {
    if (view !== "system") {
      return;
    }
    let cancelled = false;
    setDiagnostics({ kind: "loading" });
    void fetchDesktopDiagnostics(activeProfilePath)
      .then((value) => {
        if (!cancelled) {
          setDiagnostics({ kind: "ready", value });
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setDiagnostics({ kind: "error", error: asDesktopError(error) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [view, activeProfilePath]);

  function navigate(destination: NavigationItem) {
    if (!destination.available || (destination.id !== "home" && destination.id !== "system")) {
      return;
    }
    setView(destination.id);
  }

  async function handleInspect() {
    const path = profilePath.trim();
    if (!path) {
      setAction({
        kind: "error",
        error: new DesktopClientError({
          code: "profile_path_required",
          message: "Enter an absolute profile path before inspecting it.",
          retryable: false
        })
      });
      return;
    }
    setAction({ kind: "loading", message: "Inspecting the profile without changing it…" });
    try {
      const value = await inspectDesktopProfile(path);
      setInspection(value);
      setAction({
        kind: "success",
        message: value.can_open
          ? "Profile inspection passed. The profile can be opened."
          : "Profile inspection completed with findings. Nothing was changed."
      });
    } catch (error) {
      setAction({ kind: "error", error: asDesktopError(error) });
    }
  }

  async function handleCreate() {
    const path = profilePath.trim();
    if (!path) {
      setAction({
        kind: "error",
        error: new DesktopClientError({
          code: "profile_path_required",
          message: "Enter an absolute path for the new profile.",
          retryable: false
        })
      });
      return;
    }
    setAction({ kind: "loading", message: "Creating a safe local profile…" });
    try {
      const result = await createDesktopProfile(path);
      setInspection(result.profile);
      setOpenedProfile(result.profile);
      setSample(null);
      await loadBootstrap(true);
      setAction({
        kind: "success",
        message: "The local profile was created and opened with network access disabled."
      });
    } catch (error) {
      setAction({ kind: "error", error: asDesktopError(error) });
    }
  }

  async function handleOpen(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const path = profilePath.trim();
    if (!path) {
      setAction({
        kind: "error",
        error: new DesktopClientError({
          code: "profile_path_required",
          message: "Enter or select an absolute profile path before opening it.",
          retryable: false
        })
      });
      return;
    }
    setAction({ kind: "loading", message: "Validating and opening the profile…" });
    try {
      const result = await openDesktopProfile(path);
      setInspection(result.profile);
      setOpenedProfile(result.profile);
      setSample(null);
      await loadBootstrap(true);
      setAction({ kind: "success", message: "The profile passed validation and is open." });
    } catch (error) {
      setOpenedProfile(null);
      setAction({ kind: "error", error: asDesktopError(error) });
    }
  }

  async function handleKnownProfile(profile: DesktopProfileReference) {
    setAction({ kind: "loading", message: `Selecting ${profile.label}…` });
    try {
      const result = await selectDesktopProfile(profile.path);
      setProfilePath(result.selected_profile);
      setInspection(result.profile);
      setOpenedProfile(null);
      setSample(null);
      await loadBootstrap(true);
      setAction({
        kind: "success",
        message: `${profile.label} is selected but has not been opened yet.`
      });
    } catch (error) {
      setAction({ kind: "error", error: asDesktopError(error) });
    }
  }

  async function handleSampleImport() {
    if (!openedProfile) {
      return;
    }
    setAction({ kind: "loading", message: "Importing the bundled synthetic sample…" });
    try {
      const result = await importBundledSample(openedProfile.profile_root);
      setSample(result);
      setAction({
        kind: "success",
        message: "Synthetic sample data was imported locally with governed lineage."
      });
    } catch (error) {
      setAction({ kind: "error", error: asDesktopError(error) });
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>

      <aside className="app-sidebar" aria-label="Application navigation">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            O
          </div>
          <div>
            <p className="brand-name">OSCA</p>
            <p className="brand-subtitle">Local research desktop</p>
          </div>
        </div>

        <nav className="primary-navigation" aria-label="Primary">
          {navigation.map((item) =>
            item.available && (item.id === "home" || item.id === "system") ? (
              <button
                className="nav-item"
                data-active={view === item.id}
                key={item.id}
                onClick={() => navigate(item)}
                type="button"
              >
                <span>{item.label}</span>
                {view === item.id ? <span className="nav-current">Current</span> : null}
              </button>
            ) : (
              <div className="nav-item nav-item-unavailable" key={item.id}>
                <span>{item.label}</span>
                <span className="nav-later" title={item.reason}>
                  Later
                </span>
              </div>
            )
          )}
        </nav>

        <div className="sidebar-boundary">
          <StatusBadge tone="safe">Research only</StatusBadge>
          <p>No broker, exchange, autonomous, or real-capital execution path.</p>
        </div>
      </aside>

      <div className="app-workspace">
        <header className="app-header">
          <div>
            <p className="eyebrow">Desktop foundation</p>
            <p className="header-context">
              {openedProfile
                ? `Open profile: ${openedProfile.profile_root}`
                : selectedProfile
                  ? `Selected profile: ${selectedProfile}`
                  : "No profile selected"}
            </p>
          </div>
          <div className="header-status" aria-label="Application safety status">
            <StatusBadge tone="neutral">Local storage</StatusBadge>
            <StatusBadge tone="neutral">Network off</StatusBadge>
            <StatusBadge tone="safe">Live execution off</StatusBadge>
          </div>
        </header>

        <main className="main-content" id="main-content">
          {view === "home" ? (
            <HomeSurface
              action={action}
              actionErrorRef={actionErrorRef}
              bootstrap={bootstrap}
              disclosures={disclosures}
              inspection={inspection}
              onCreate={handleCreate}
              onInspect={handleInspect}
              onKnownProfile={handleKnownProfile}
              onOpen={handleOpen}
              onPathChange={setProfilePath}
              onRetryBootstrap={() => void loadBootstrap()}
              onSampleImport={handleSampleImport}
              openedProfile={openedProfile}
              profilePath={profilePath}
              sample={sample}
              titleRef={mainHeadingRef}
            />
          ) : (
            <SystemSurface
              diagnostics={diagnostics}
              onRetry={() => {
                setDiagnostics({ kind: "loading" });
                void fetchDesktopDiagnostics(activeProfilePath)
                  .then((value) => setDiagnostics({ kind: "ready", value }))
                  .catch((error) =>
                    setDiagnostics({ kind: "error", error: asDesktopError(error) })
                  );
              }}
              titleRef={mainHeadingRef}
            />
          )}
        </main>

        <SafetyBoundary disclosures={disclosures} />
      </div>
    </div>
  );
}

type HomeSurfaceProps = {
  action: ActionState;
  actionErrorRef: React.RefObject<HTMLDivElement | null>;
  bootstrap: AsyncState<DesktopBootstrap>;
  disclosures: DesktopDisclosures;
  inspection: ProfileInspection | null;
  onCreate: () => Promise<void>;
  onInspect: () => Promise<void>;
  onKnownProfile: (profile: DesktopProfileReference) => Promise<void>;
  onOpen: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onPathChange: (value: string) => void;
  onRetryBootstrap: () => void;
  onSampleImport: () => Promise<void>;
  openedProfile: ProfileInspection | null;
  profilePath: string;
  sample: SampleImportResult | null;
  titleRef: React.RefObject<HTMLHeadingElement | null>;
};

function HomeSurface({
  action,
  actionErrorRef,
  bootstrap,
  disclosures,
  inspection,
  onCreate,
  onInspect,
  onKnownProfile,
  onOpen,
  onPathChange,
  onRetryBootstrap,
  onSampleImport,
  openedProfile,
  profilePath,
  sample,
  titleRef
}: HomeSurfaceProps) {
  if (bootstrap.kind === "loading") {
    return (
      <PageFrame title="Preparing OSCA" titleRef={titleRef}>
        <StatePanel
          description="Loading versioned desktop state from the Python application service."
          kind="loading"
          title="Loading your local workspace"
        />
      </PageFrame>
    );
  }

  if (bootstrap.kind === "error") {
    return (
      <PageFrame title="OSCA is unavailable" titleRef={titleRef}>
        <StatePanel
          action={bootstrap.error.retryable ? onRetryBootstrap : undefined}
          actionLabel="Retry"
          description={bootstrap.error.message}
          kind="error"
          title="The desktop application service could not be loaded"
        />
      </PageFrame>
    );
  }

  const value = bootstrap.value;
  return (
    <PageFrame
      intro={
        value.first_run_required
          ? "Create or open a validated local profile to begin an offline research workspace."
          : "Open a validated profile, inspect system readiness, or import the bundled synthetic sample."
      }
      title={value.first_run_required ? "Welcome to OSCA" : "Research home"}
      titleRef={titleRef}
    >
      {value.first_run_required ? <OnboardingDisclosure disclosures={disclosures} /> : null}

      <ActionFeedback action={action} errorRef={actionErrorRef} />

      <div className="content-grid">
        <section className="panel panel-primary" aria-labelledby="profile-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Local profile</p>
              <h2 id="profile-heading">Choose where OSCA stores your work</h2>
            </div>
            {openedProfile ? <StatusBadge tone="safe">Open</StatusBadge> : null}
          </div>

          <form className="profile-form" onSubmit={(event) => void onOpen(event)}>
            <label htmlFor="profile-path">Absolute profile path</label>
            <input
              autoComplete="off"
              id="profile-path"
              onChange={(event) => onPathChange(event.target.value)}
              placeholder="/Users/you/Documents/OSCA-profile"
              spellCheck={false}
              type="text"
              value={profilePath}
            />
            <p className="field-help">
              The path is sent to the Python application service for validation. The frontend does
              not browse, inspect, or create files directly.
            </p>
            <div className="button-row">
              <button className="button button-secondary" onClick={() => void onInspect()} type="button">
                Inspect only
              </button>
              <button className="button button-secondary" onClick={() => void onCreate()} type="button">
                Create new profile
              </button>
              <button className="button button-primary" type="submit">
                Open validated profile
              </button>
            </div>
          </form>

          {value.profiles.length > 0 ? (
            <div className="known-profiles">
              <h3>Known profiles</h3>
              <ul className="profile-list">
                {value.profiles.map((profile) => (
                  <li key={profile.path}>
                    <div>
                      <strong>{profile.label}</strong>
                      <span>{profile.path}</span>
                      <small>
                        {profile.last_opened_at
                          ? `Last opened ${formatTimestamp(profile.last_opened_at)}`
                          : "Selected previously, not yet opened"}
                      </small>
                    </div>
                    <button
                      className="button button-quiet"
                      onClick={() => void onKnownProfile(profile)}
                      type="button"
                    >
                      Select
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>

        <section className="panel" aria-labelledby="inspection-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Read-only check</p>
              <h2 id="inspection-heading">Profile inspection</h2>
            </div>
            {inspection ? (
              <StatusBadge tone={inspection.can_open ? "safe" : "warning"}>
                {inspection.can_open ? "Can open" : "Needs attention"}
              </StatusBadge>
            ) : null}
          </div>
          {inspection ? (
            <ProfileSummary profile={inspection} />
          ) : (
            <EmptyState
              description="Inspect a path to see compatibility, storage, writability, and lock findings without changing it."
              title="No profile inspected"
            />
          )}
        </section>
      </div>

      <section className="panel sample-panel" aria-labelledby="sample-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Offline first run</p>
            <h2 id="sample-heading">Bundled synthetic sample</h2>
          </div>
          <StatusBadge tone="neutral">No network</StatusBadge>
        </div>
        <p>
          Import ten deterministic synthetic daily observations through OSCA's canonical Python
          import service. The sample is labelled synthetic, retains lineage, and requires no
          provider account or credential.
        </p>
        {openedProfile ? (
          <button
            className="button button-primary"
            onClick={() => void onSampleImport()}
            type="button"
          >
            Import synthetic sample
          </button>
        ) : (
          <p className="inline-guidance">Open a validated profile to enable sample import.</p>
        )}
        {sample ? <SampleSummary sample={sample} /> : null}
      </section>
    </PageFrame>
  );
}

type SystemSurfaceProps = {
  diagnostics: AsyncState<DesktopDiagnostics>;
  onRetry: () => void;
  titleRef: React.RefObject<HTMLHeadingElement | null>;
};

function SystemSurface({ diagnostics, onRetry, titleRef }: SystemSurfaceProps) {
  return (
    <PageFrame
      intro="Inspect sidecar, package, profile, provider, network, recommendation, and execution boundaries."
      title="System diagnostics"
      titleRef={titleRef}
    >
      {diagnostics.kind === "loading" ? (
        <StatePanel
          description="Requesting bounded diagnostics from the Python application service."
          kind="loading"
          title="Loading diagnostics"
        />
      ) : diagnostics.kind === "error" ? (
        <StatePanel
          action={diagnostics.error.retryable ? onRetry : undefined}
          actionLabel="Retry diagnostics"
          description={diagnostics.error.message}
          kind="error"
          title="Diagnostics are unavailable"
        />
      ) : (
        <div className="diagnostics-grid">
          <section className="panel" aria-labelledby="runtime-heading">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Runtime</p>
                <h2 id="runtime-heading">Application service</h2>
              </div>
              <StatusBadge tone="safe">{diagnostics.value.sidecar_status}</StatusBadge>
            </div>
            <DefinitionGrid
              entries={[
                ["Protocol", diagnostics.value.protocol_version],
                ["OSCA version", displayValue(diagnostics.value.package.osca_version)],
                ["Python", displayValue(diagnostics.value.package.python_version)],
                [
                  "Platform",
                  `${displayValue(diagnostics.value.package.platform_system)} ${displayValue(
                    diagnostics.value.package.platform_machine
                  )}`
                ]
              ]}
            />
          </section>

          <section className="panel" aria-labelledby="safety-heading">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Safety</p>
                <h2 id="safety-heading">Capability boundaries</h2>
              </div>
              <StatusBadge tone="safe">Fail closed</StatusBadge>
            </div>
            <DefinitionGrid
              entries={[
                ["Network", diagnostics.value.network_policy],
                ["Providers", diagnostics.value.provider_status],
                [
                  "Recommendations",
                  diagnostics.value.recommendations_enabled ? "Enabled" : "Unavailable"
                ],
                [
                  "Live execution",
                  diagnostics.value.live_execution_enabled ? "Enabled" : "Disabled"
                ]
              ]}
            />
          </section>

          <section className="panel diagnostics-profile" aria-labelledby="diagnostic-profile-heading">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Selected profile</p>
                <h2 id="diagnostic-profile-heading">Profile readiness</h2>
              </div>
            </div>
            {diagnostics.value.profile ? (
              <ProfileSummary profile={diagnostics.value.profile} />
            ) : (
              <EmptyState
                description="Select or open a profile from Home to include profile diagnostics."
                title="No profile selected"
              />
            )}
          </section>
        </div>
      )}
    </PageFrame>
  );
}

function OnboardingDisclosure({ disclosures }: { disclosures: DesktopDisclosures }) {
  const items = useMemo(
    () => [
      ["Research only", disclosures.research_only],
      ["Local storage", disclosures.local_storage],
      ["Optional network", disclosures.optional_network],
      ["Provider-free sample", disclosures.providers],
      ["Credentials", disclosures.credentials],
      ["Recommendations", disclosures.recommendations],
      ["Live execution", disclosures.live_execution]
    ],
    [disclosures]
  );

  return (
    <section className="onboarding-disclosure" aria-labelledby="before-you-begin">
      <div>
        <p className="eyebrow">Before you begin</p>
        <h2 id="before-you-begin">Know the product boundaries</h2>
      </div>
      <ul>
        {items.map(([title, description]) => (
          <li key={title}>
            <strong>{title}</strong>
            <span>{description}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ProfileSummary({ profile }: { profile: ProfileInspection }) {
  return (
    <div className="profile-summary">
      <DefinitionGrid
        entries={[
          ["Profile", profile.profile_root],
          ["Configured", profile.configured ? "Yes" : "No"],
          ["Writable", profile.writable ? "Yes" : "No"],
          ["Lock", profile.lock_state],
          ["Compatibility", profile.compatibility_status],
          ["Storage", profile.storage_root ?? "Unavailable"]
        ]}
      />
      {profile.findings.length > 0 ? (
        <div className="findings" aria-label="Profile findings">
          <h3>Findings</h3>
          <ul>
            {profile.findings.map((finding) => (
              <li key={`${finding.check_id}-${finding.message}`}>
                <strong>{finding.message}</strong>
                {finding.remediation ? <span>{finding.remediation}</span> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="success-message">No blocking profile findings.</p>
      )}
    </div>
  );
}

function SampleSummary({ sample }: { sample: SampleImportResult }) {
  return (
    <div className="sample-summary" role="status">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Imported</p>
          <h3>{sample.sample_label}</h3>
        </div>
        <StatusBadge tone="safe">Synthetic</StatusBadge>
      </div>
      <DefinitionGrid
        entries={[
          ["Dataset revision", sample.import.dataset_revision_id],
          ["Symbol", sample.import.symbol],
          ["Rows", String(sample.import.row_count)],
          ["Timeframe", sample.import.timeframe],
          ["Network used", sample.network_access_enabled ? "Yes" : "No"],
          ["Credential required", sample.credential_required ? "Yes" : "No"]
        ]}
      />
    </div>
  );
}

function ActionFeedback({
  action,
  errorRef
}: {
  action: ActionState;
  errorRef: React.RefObject<HTMLDivElement | null>;
}) {
  if (action.kind === "idle") {
    return <div aria-live="polite" className="sr-only" />;
  }
  if (action.kind === "error") {
    return (
      <div
        className="action-feedback action-feedback-error"
        ref={errorRef}
        role="alert"
        tabIndex={-1}
      >
        <strong>Action failed: {action.error.code}</strong>
        <span>{action.error.message}</span>
        <small>{action.error.retryable ? "This action can be retried." : "Review the guidance before trying again."}</small>
      </div>
    );
  }
  return (
    <div
      aria-live="polite"
      className={`action-feedback ${action.kind === "success" ? "action-feedback-success" : ""}`}
      role="status"
    >
      <span>{action.message}</span>
    </div>
  );
}

function PageFrame({
  children,
  intro,
  title,
  titleRef
}: {
  children: ReactNode;
  intro?: string;
  title: string;
  titleRef: React.RefObject<HTMLHeadingElement | null>;
}) {
  return (
    <div className="page-frame">
      <div className="page-heading">
        <h1 ref={titleRef} tabIndex={-1}>
          {title}
        </h1>
        {intro ? <p>{intro}</p> : null}
      </div>
      {children}
    </div>
  );
}

function StatePanel({
  action,
  actionLabel,
  description,
  kind,
  title
}: {
  action?: () => void;
  actionLabel?: string;
  description: string;
  kind: "loading" | "empty" | "unavailable" | "error";
  title: string;
}) {
  return (
    <section className={`state-panel state-panel-${kind}`} role={kind === "error" ? "alert" : "status"}>
      <div className="state-icon" aria-hidden="true">
        {kind === "loading" ? "…" : kind === "error" ? "!" : "○"}
      </div>
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
        {action && actionLabel ? (
          <button className="button button-primary" onClick={action} type="button">
            {actionLabel}
          </button>
        ) : null}
      </div>
    </section>
  );
}

function EmptyState({ description, title }: { description: string; title: string }) {
  return (
    <div className="empty-state">
      <div aria-hidden="true">○</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function DefinitionGrid({ entries }: { entries: Array<[string, string]> }) {
  return (
    <dl className="definition-grid">
      {entries.map(([term, description]) => (
        <div key={term}>
          <dt>{term}</dt>
          <dd>{description}</dd>
        </div>
      ))}
    </dl>
  );
}

function StatusBadge({ children, tone }: { children: ReactNode; tone: "safe" | "neutral" | "warning" }) {
  return <span className={`status-badge status-badge-${tone}`}>{children}</span>;
}

function SafetyBoundary({ disclosures }: { disclosures: DesktopDisclosures }) {
  return (
    <footer className="safety-boundary" aria-label="Permanent product boundaries">
      <strong>{disclosures.research_only}</strong>
      <span>{disclosures.optional_network}</span>
      <span>{disclosures.live_execution}</span>
    </footer>
  );
}

function asDesktopError(error: unknown): DesktopClientError {
  if (error instanceof DesktopClientError) {
    return error;
  }
  return new DesktopClientError({
    code: "unexpected_application_error",
    message: error instanceof Error ? error.message : "An unexpected application error occurred.",
    retryable: true
  });
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function displayValue(value: unknown): string {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return "Unknown";
}
