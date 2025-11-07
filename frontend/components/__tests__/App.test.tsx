/**
 * Tests for the main App component.
 */

import { render, screen } from "@testing-library/react";
import App from "../App";

describe("App", () => {
  it("renders without crashing", () => {
    render(<App />);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("renders the sidebar", () => {
    render(<App />);
    // Sidebar should be present (adjust selector based on actual implementation)
    expect(
      document.querySelector('[data-testid="sidebar"]') || document.querySelector("aside")
    ).toBeInTheDocument();
  });
});
