/**
 * Zustand global state management for Growgent frontend.
 *
 * Manages global application state such as current farm, filters, and UI preferences.
 * @module store
 */

import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import type { Page } from "../types";

/**
 * Global application state interface.
 */
interface AppState {
  /** Current active page */
  currentPage: Page;
  /** Currently selected farm ID */
  selectedFarmId: string | null;
  /** Currently selected field ID */
  selectedFieldId: string | null;
  /** Sidebar collapsed state */
  sidebarCollapsed: boolean;
  /** Alert filters */
  alertFilters: {
    severity: "all" | "critical" | "warning" | "info";
    sortBy: "newest" | "oldest" | "severity" | "field";
  };
  /** Map layer visibility state */
  mapLayers: {
    satellite: boolean;
    sensors: boolean;
    ndvi: boolean;
    fireRisk: boolean;
    psps: boolean;
  };
  /** Actions */
  setCurrentPage: (page: Page) => void;
  setSelectedFarmId: (farmId: string | null) => void;
  setSelectedFieldId: (fieldId: string | null) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setAlertFilters: (filters: Partial<AppState["alertFilters"]>) => void;
  setMapLayers: (layers: Partial<AppState["mapLayers"]>) => void;
}

/**
 * Global application store using Zustand.
 *
 * Uses persist middleware to save UI preferences to localStorage.
 */
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        currentPage: "dashboard",
        selectedFarmId: null,
        selectedFieldId: null,
        sidebarCollapsed: false,
        alertFilters: {
          severity: "all",
          sortBy: "newest",
        },
        mapLayers: {
          satellite: true,
          sensors: true,
          ndvi: false,
          fireRisk: true,
          psps: true,
        },
        // Actions
        setCurrentPage: (page) => set({ currentPage: page }),
        setSelectedFarmId: (farmId) => set({ selectedFarmId: farmId }),
        setSelectedFieldId: (fieldId) => set({ selectedFieldId: fieldId }),
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        setAlertFilters: (filters) =>
          set((state) => ({
            alertFilters: { ...state.alertFilters, ...filters },
          })),
        setMapLayers: (layers) =>
          set((state) => ({
            mapLayers: { ...state.mapLayers, ...layers },
          })),
      }),
      {
        name: "growgent-app-store",
        // Only persist UI preferences, not data
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          alertFilters: state.alertFilters,
          mapLayers: state.mapLayers,
        }),
      }
    ),
    { name: "GrowgentAppStore" }
  )
);

