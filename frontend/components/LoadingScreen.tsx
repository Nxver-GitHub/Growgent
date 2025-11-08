/**
 * LoadingScreen component displays an interactive loading indicator.
 *
 * Shows a progress bar and animated spinner to indicate the application is loading.
 * Prevents users from accidentally refreshing by showing clear loading state.
 *
 * @component
 * @returns {JSX.Element} The loading screen
 */
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

export function LoadingScreen(): JSX.Element {
  const [progress, setProgress] = useState(0);
  const [dots, setDots] = useState("");

  useEffect(() => {
    // Simulate progress (0-90%, then wait for app to load)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 90) {
          return prev + Math.random() * 15;
        }
        return prev;
      });
    }, 200);

    // Animate dots
    const dotsInterval = setInterval(() => {
      setDots((prev) => {
        if (prev === "...") return "";
        return prev + ".";
      });
    }, 500);

    return () => {
      clearInterval(interval);
      clearInterval(dotsInterval);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-[9999] bg-white flex flex-col items-center justify-center">
      <div className="text-center space-y-8 max-w-md px-8">
        {/* Logo/Brand */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-emerald-500 rounded-lg flex items-center justify-center">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-emerald-600">Growgent</h1>
        </div>

        {/* Animated Spinner */}
        <div className="flex justify-center">
          <Loader2 className="h-12 w-12 animate-spin text-emerald-600" />
        </div>

        {/* Loading Text */}
        <div className="space-y-2">
          <p className="text-lg font-medium text-slate-900">
            Loading your farm dashboard{dots}
          </p>
          <p className="text-sm text-slate-500">
            Connecting to AI agents and sensors...
          </p>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-emerald-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 text-center">
            {Math.round(Math.min(progress, 100))}%
          </p>
        </div>

        {/* Helpful Message */}
        <div className="pt-4 border-t border-slate-200">
          <p className="text-xs text-slate-400">
            Please wait while we initialize your dashboard. Do not refresh the page.
          </p>
        </div>
      </div>
    </div>
  );
}

