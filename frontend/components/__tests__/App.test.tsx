/**
 * Tests for the main App component.
 */

import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../../App";

jest.mock("../../lib/api", () => ({
  queryClient: new QueryClient(), // Mock the exported queryClient instance
  alertsApi: {
    getCriticalAlerts: jest.fn().mockResolvedValue({ alerts: [], count: 0 }),
  },
  recommendationsApi: {
    getRecommendations: jest.fn().mockResolvedValue({ recommendations: [], total: 0 }),
  },
  dashboardApi: {
    getDashboard: jest.fn().mockResolvedValue({
      criticalAlerts: [],
      recentRecommendations: [],
      fields: [],
    }),
  },
}));

jest.mock("../../lib/constants", () => ({
  POLLING_INTERVALS: {
    ALERTS: 30000, // 30 seconds
  },
}));

jest.mock("../../lib/hooks/useAlerts", () => ({
  useCriticalAlerts: jest.fn().mockReturnValue({ data: { alerts: [], count: 0 }, error: null }),
}));

jest.mock("../../lib/hooks/useRecommendations", () => ({
  useRecommendations: jest.fn().mockReturnValue({ data: { recommendations: [], total: 0 }, error: null }),
  useAcceptRecommendation: jest.fn().mockReturnValue({ mutate: jest.fn() }),
}));

jest.mock("../../lib/hooks/useDashboard", () => ({
  useDashboard: jest.fn().mockReturnValue({ data: null, error: null }),
}));


describe("App", () => {
  const queryClient = new QueryClient();

  it("renders without crashing", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("renders the sidebar", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );
    // Sidebar should be present (adjust selector based on actual implementation)
    expect(
      document.querySelector('[data-testid="sidebar"]') || document.querySelector("aside")
    ).toBeInTheDocument();
  });
});
