/**
 * Main entry point for the Growgent frontend application.
 *
 * This file initializes the React application and mounts it to the DOM.
 * @module main
 */

import { createRoot, Root } from "react-dom/client";
import { StrictMode } from "react";
import App from "./App.tsx";
import { LoadingScreen } from "./components/LoadingScreen.tsx";
import "./index.css";
import "mapbox-gl/dist/mapbox-gl.css";

// Initialize application
const rootElement: HTMLElement | null = document.getElementById("root");

if (!rootElement) {
  const error = "Failed to find root element. Make sure there is a <div id='root'></div> in your HTML.";
  if (process.env.NODE_ENV === "development") {
    console.error("❌", error);
}
  throw new Error(error);
}

try {
const root: Root = createRoot(rootElement);
  
  // Show loading screen immediately
  root.render(
    <StrictMode>
      <LoadingScreen />
    </StrictMode>
  );
  
  // Small delay to ensure loading screen is visible, then render app
  // Note: StrictMode disabled to prevent double-rendering issues in development
  setTimeout(() => {
    root.render(
      <App />
    );
  }, 100);
  
} catch (error) {
  console.error("❌ Failed to render application:", error);
  
  // Show user-friendly error message
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; padding: 2rem; font-family: system-ui, sans-serif;">
        <h1 style="color: #ef4444; margin-bottom: 1rem;">Application Error</h1>
        <p style="color: #64748b; margin-bottom: 2rem;">Failed to load the application. Please check the browser console for details.</p>
        <button onclick="window.location.reload()" style="padding: 0.75rem 1.5rem; background: #10b981; color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
          Reload Page
        </button>
        <pre style="margin-top: 2rem; padding: 1rem; background: #f1f5f9; border-radius: 0.5rem; overflow: auto; max-width: 800px; text-align: left;">
          ${error instanceof Error ? error.message : String(error)}
        </pre>
      </div>
    `;
  }
  throw error;
}
