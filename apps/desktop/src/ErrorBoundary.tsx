import { Component, ErrorInfo, ReactNode } from "react";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  failed: boolean;
};

export class AppErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("OSCA desktop rendering failure", {
      name: error.name,
      componentStack: info.componentStack
    });
  }

  render() {
    if (!this.state.failed) {
      return this.props.children;
    }

    return (
      <main className="fatal-error" id="main-content">
        <section aria-labelledby="fatal-error-heading" role="alert">
          <p className="eyebrow">Application error</p>
          <h1 id="fatal-error-heading">OSCA could not render this screen</h1>
          <p>
            No profile, provider, recommendation, or execution state is being inferred. Reload the
            desktop application and use System diagnostics if the problem continues.
          </p>
          <button className="button button-primary" onClick={() => window.location.reload()} type="button">
            Reload OSCA
          </button>
        </section>
        <footer className="safety-boundary" aria-label="Permanent product boundaries">
          <strong>OSCA is research and simulation software, not financial advice.</strong>
          <span>Network access is optional and must be enabled explicitly.</span>
          <span>Broker, exchange, autonomous, and real-capital execution are disabled.</span>
        </footer>
      </main>
    );
  }
}
