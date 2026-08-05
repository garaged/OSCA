import { useEffect, useState } from "react";
import { requestDesktop, type DesktopResponse } from "./api";

export function App() {
  const [health, setHealth] = useState<DesktopResponse | null>(null);
  const [failure, setFailure] = useState<string | null>(null);

  useEffect(() => {
    requestDesktop("system.health")
      .then(setHealth)
      .catch((error: unknown) => {
        setFailure(error instanceof Error ? error.message : "Desktop API unavailable");
      });
  }, []);

  const ready = health?.status === "ok";

  return (
    <main>
      <header>
        <p className="eyebrow">Local-first market research</p>
        <h1>OSCA Desktop</h1>
        <p>
          Developer preview of the supervised desktop architecture. Financial calculations
          remain authoritative in the Python application core.
        </p>
      </header>

      <section aria-labelledby="status-heading">
        <h2 id="status-heading">System status</h2>
        <dl>
          <div><dt>Desktop API</dt><dd>{failure ? "Unavailable" : ready ? "Ready" : "Starting"}</dd></div>
          <div><dt>Protocol</dt><dd>{String(health?.result?.protocol_version ?? "1.0")}</dd></div>
          <div><dt>Live execution</dt><dd>Disabled</dd></div>
        </dl>
        {failure && <p role="alert">{failure}</p>}
      </section>

      <nav aria-label="Product areas">
        {[
          "Discover",
          "Research",
          "Simulate",
          "Monitor",
          "Evidence",
          "System"
        ].map((area) => <button key={area} disabled>{area}</button>)}
      </nav>
    </main>
  );
}
