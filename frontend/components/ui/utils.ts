/**
 * Utility function for merging Tailwind CSS class names.
 *
 * Combines clsx and tailwind-merge to handle conditional classes and resolve conflicts.
 *
 * @param {...ClassValue[]} inputs - Class values to merge
 * @returns {string} Merged class string
 */
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
