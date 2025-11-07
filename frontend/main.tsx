/**
 * Main entry point for the Growgent frontend application.
 *
 * This file initializes the React application and mounts it to the DOM.
 * @module main
 */

import { createRoot, Root } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

const rootElement: HTMLElement | null = document.getElementById("root");

if (!rootElement) {
  throw new Error(
    "Failed to find root element. Make sure there is a <div id='root'></div> in your HTML."
  );
}

const root: Root = createRoot(rootElement);
root.render(<App />);
