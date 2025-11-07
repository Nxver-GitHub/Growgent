/**
 * Shared TypeScript type definitions for the Growgent frontend.
 *
 * This module contains common types and interfaces used across components.
 * @module types
 */

/**
 * Recommendation data structure from agents.
 */
export interface Recommendation {
  /** Name of the agent that generated the recommendation */
  agent: string;
  /** Title of the recommendation */
  title: string;
  /** Confidence score (0-100) */
  confidence: number;
  /** Detailed reason for the recommendation */
  reason: string;
  /** List of field names affected */
  fields: string[];
  /** Optional duration of the recommended action */
  duration?: string;
  /** Optional water volume required */
  waterVolume?: string;
  /** Optional fire risk impact description */
  fireRiskImpact?: string;
  /** Optional water savings description */
  waterSaved?: string;
}

/**
 * Page navigation types.
 */
export type Page =
  | "dashboard"
  | "schedule"
  | "fields"
  | "fire-risk"
  | "metrics"
  | "alerts"
  | "chat"
  | "settings";

/**
 * Agent status types.
 */
export type AgentStatus = "active" | "warning" | "error";

/**
 * Alert severity levels.
 */
export type AlertSeverity = "critical" | "warning" | "info";

/**
 * Metric trend direction.
 */
export type TrendDirection = "up" | "down" | "neutral";
