import React from "react";
import ReactDOM from "react-dom/client";
import { D3Root } from "./D3Root";
import { AppErrorBoundary } from "./ErrorBoundary";
import "./styles.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("OSCA desktop root element is missing");
}

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <AppErrorBoundary>
      <D3Root />
    </AppErrorBoundary>
  </React.StrictMode>
);
