/**
 * IrrigationSchedule component displays and manages irrigation scheduling.
 *
 * Shows calendar view of scheduled irrigation events with filtering and editing capabilities.
 *
 * @component
 * @returns {JSX.Element} The irrigation schedule view
 */
import { useState, useMemo } from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Calendar, ChevronLeft, ChevronRight, Download, X } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { toast } from "sonner";
import { useRecommendations } from "../lib/hooks/useRecommendations";
import { useFields } from "../lib/hooks/useFields";
import type { Recommendation } from "../lib/types";
import { formatTime } from "../lib/utils/formatters";

interface IrrigationEvent {
  /** Field name where irrigation occurs */
  field: string;
  /** Time of irrigation */
  time: string;
  /** Type of irrigation event */
  type: "scheduled" | "recommended" | "completed" | "psps-prep";
  /** Optional duration */
  duration?: string;
  /** Optional water volume */
  waterVolume?: string;
  /** Optional date for display */
  date?: number;
}

export function IrrigationSchedule(): JSX.Element {
  const [view, setView] = useState<"week" | "month">("week");
  const [selectedEvent, setSelectedEvent] = useState<IrrigationEvent | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedField, setSelectedField] = useState<string>("all-fields");
  const [selectedCrop, setSelectedCrop] = useState<string>("all-crops");

  // Fetch recommendations and fields from API
  const { data: recommendationsData, isLoading: isLoadingRecs } = useRecommendations({
    accepted: false, // Show pending recommendations
    page: 1,
    page_size: 50,
  });
  const { data: fieldsData, isLoading: isLoadingFields } = useFields();

  // Transform recommendations into calendar events
  const eventsByDate = useMemo(() => {
    if (!recommendationsData?.recommendations) return {};

    const events: Record<string, IrrigationEvent[]> = {};

    recommendationsData.recommendations.forEach((rec: Recommendation) => {
      if (!rec.recommended_timing) return;

      const date = new Date(rec.recommended_timing);
      const dateKey = date.toISOString().split("T")[0]; // YYYY-MM-DD
      const fieldName = fieldsData?.fields.find((f) => f.id === rec.field_id)?.name || rec.field_id;

      const event: IrrigationEvent = {
        field: fieldName,
        time: formatTime(rec.recommended_timing),
        type: rec.psps_alert 
          ? ("psps-prep" as const) 
          : rec.accepted 
          ? ("completed" as const) 
          : ("recommended" as const),
        duration: rec.zones_affected || undefined,
        waterVolume: rec.water_saved_liters
          ? `${rec.water_saved_liters.toLocaleString()} liters`
          : undefined,
      };

      if (dateKey) {
        if (!events[dateKey]) {
          events[dateKey] = [];
        }
        events[dateKey].push(event);
      }
    });

    return events;
  }, [recommendationsData, fieldsData]);

  // Get current week dates
  const today = new Date();
  const currentWeekStart = new Date(today);
  currentWeekStart.setDate(today.getDate() - today.getDay() + 1); // Monday

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const currentWeek = useMemo(() => {
    return weekDays.map((_, index) => {
      const date = new Date(currentWeekStart);
      date.setDate(currentWeekStart.getDate() + index);
      const dateKey = date.toISOString().split("T")[0];
      const dayEvents = (dateKey && eventsByDate[dateKey]) ? eventsByDate[dateKey] : [];

      return {
        date: date.getDate(),
        dateKey: dateKey || "",
        events: dayEvents,
      };
    });
  }, [currentWeekStart, eventsByDate]);

  // Show skeleton loaders while loading
  if ((isLoadingRecs || isLoadingFields) && !recommendationsData && !fieldsData) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-slate-200 rounded animate-pulse" />
        <div className="grid grid-cols-7 gap-2">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <div key={i} className="h-48 bg-slate-200 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const eventColors: Record<IrrigationEvent["type"], string> = {
    recommended: "bg-emerald-100 border-emerald-500 text-emerald-700",
    "psps-prep": "bg-amber-100 border-amber-500 text-amber-700",
    completed: "bg-green-100 border-green-500 text-green-700",
    scheduled: "bg-blue-100 border-blue-500 text-blue-700",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2>Irrigation Schedule & Planning</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success("PDF export started. Check your downloads.")}
          >
            <Download className="h-4 w-4 mr-2" />
            Export as PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success("Calendar file downloaded. Import to your calendar app.")}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Export as ICS
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex gap-2">
          <Button variant={view === "week" ? "default" : "outline"} onClick={() => setView("week")}>
            Week
          </Button>
          <Button
            variant={view === "month" ? "default" : "outline"}
            onClick={() => setView("month")}
          >
            Month
          </Button>
        </div>

        <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
          {showFilters ? "Hide" : "Show"} Filters
        </Button>
      </div>

      {/* Collapsible Filters */}
      {showFilters && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h4>Filters</h4>
            <Button variant="ghost" size="sm" onClick={() => setShowFilters(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-4">
            <Select value={selectedCrop} onValueChange={setSelectedCrop}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by crop" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-crops">All Crops</SelectItem>
                {fieldsData?.fields
                  .map((f) => f.crop_type)
                  .filter((crop, index, self) => self.indexOf(crop) === index)
                  .map((crop) => (
                    <SelectItem key={crop} value={crop.toLowerCase()}>
                      {crop}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>

            <Select value={selectedField} onValueChange={setSelectedField}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by field" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-fields">All Fields</SelectItem>
                {fieldsData?.fields.map((field) => (
                  <SelectItem key={field.id} value={field.id}>
                    {field.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={() => toast.success("Filters reset")}>
              Reset Filters
            </Button>
          </div>
        </Card>
      )}

      {/* Week Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous Week
        </Button>
        <h3>November 4-10, 2024</h3>
        <Button variant="outline" size="sm">
          Next Week
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-4">
        {weekDays.map((day, index) => (
          <div key={day} className="space-y-2">
            <div className="text-center p-2 bg-slate-100 rounded-lg">
              <p className="text-slate-600">{day}</p>
              <p className="text-slate-900">{currentWeek[index]?.date || ""}</p>
            </div>

            <Card className="p-4 min-h-[200px] space-y-2">
              {!currentWeek[index] || currentWeek[index].events.length === 0 ? (
                <p className="text-slate-400 text-center mt-8">No events</p>
              ) : (
                currentWeek[index]?.events.map((event: IrrigationEvent, eventIdx: number) => (
                  <div
                    key={eventIdx}
                    className={`p-3 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-shadow ${
                      eventColors[event.type]
                    }`}
                    onClick={() => setSelectedEvent({ ...event, date: currentWeek[index]?.date })}
                  >
                    <p className="mb-1">{event.field}</p>
                    <p className="text-slate-600">{event.time}</p>
                    {event.type === "psps-prep" && (
                      <Badge variant="destructive" className="mt-2">
                        PSPS
                      </Badge>
                    )}
                  </div>
                ))
              )}
            </Card>
          </div>
        ))}
      </div>

      {/* Legend */}
      <Card className="p-6">
        <h4 className="mb-4">Event Types</h4>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-emerald-500 rounded" />
            <span className="text-slate-700">Recommended</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-amber-500 rounded" />
            <span className="text-slate-700">Pre-PSPS Watering</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded" />
            <span className="text-slate-700">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded" />
            <span className="text-slate-700">PSPS Event</span>
          </div>
        </div>
      </Card>

      {/* Event Detail Modal */}
      <Dialog open={!!selectedEvent} onOpenChange={() => setSelectedEvent(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Irrigation Event Details</DialogTitle>
            <DialogDescription>
              {selectedEvent && `November ${selectedEvent.date}, 2024`}
            </DialogDescription>
          </DialogHeader>

          {selectedEvent && (
            <div className="space-y-4">
              <div>
                <p className="text-slate-600 mb-1">Field</p>
                <p className="text-slate-900">{selectedEvent.field}</p>
              </div>
              <div>
                <p className="text-slate-600 mb-1">Time</p>
                <p className="text-slate-900">{selectedEvent.time}</p>
              </div>
              <div>
                <p className="text-slate-600 mb-1">Type</p>
                <Badge className="capitalize">{selectedEvent.type.replace("-", " ")}</Badge>
              </div>
              {selectedEvent.duration && (
                <div>
                  <p className="text-slate-600 mb-1">Zones/Duration</p>
                  <p className="text-slate-900">{selectedEvent.duration}</p>
                </div>
              )}
              {selectedEvent.waterVolume && (
              <div className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-slate-700">Water volume: {selectedEvent.waterVolume}</p>
              </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedEvent(null)}>
              Close
            </Button>
            <Button
              onClick={() => {
                toast.success("Irrigation event accepted");
                setSelectedEvent(null);
              }}
            >
              Accept Recommendation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
