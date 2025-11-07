import { useState } from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Calendar, ChevronLeft, ChevronRight, Download, X } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { toast } from "sonner";

export function IrrigationSchedule() {
  const [view, setView] = useState<"week" | "month">("week");
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [showFilters, setShowFilters] = useState(false);
  
  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const currentWeek = [
    { date: 4, events: [{ field: "Field 1", time: "06:00", type: "recommended" }] },
    { date: 5, events: [] },
    { date: 6, events: [{ field: "Field 2", time: "07:00", type: "psps-prep" }] },
    { date: 7, events: [{ field: "Field 3", time: "06:30", type: "completed" }] },
    { date: 8, events: [] },
    { date: 9, events: [{ field: "Field 1", time: "14:00", type: "warning", label: "PSPS" }] },
    { date: 10, events: [] },
  ];

  const eventColors = {
    recommended: "bg-emerald-100 border-emerald-500 text-emerald-700",
    "psps-prep": "bg-amber-100 border-amber-500 text-amber-700",
    completed: "bg-green-100 border-green-500 text-green-700",
    warning: "bg-red-100 border-red-500 text-red-700",
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
          <Button
            variant={view === "week" ? "default" : "outline"}
            onClick={() => setView("week")}
          >
            Week
          </Button>
          <Button
            variant={view === "month" ? "default" : "outline"}
            onClick={() => setView("month")}
          >
            Month
          </Button>
        </div>

        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? "Hide" : "Show"} Filters
        </Button>
      </div>

      {/* Collapsible Filters */}
      {showFilters && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h4>Filters</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-4">
            <Select defaultValue="all-crops">
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by crop" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-crops">All Crops</SelectItem>
                <SelectItem value="strawberry">Strawberry</SelectItem>
                <SelectItem value="lettuce">Lettuce</SelectItem>
                <SelectItem value="tomato">Tomato</SelectItem>
              </SelectContent>
            </Select>

            <Select defaultValue="all-fields">
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by field" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-fields">All Fields</SelectItem>
                <SelectItem value="field-1">Field 1</SelectItem>
                <SelectItem value="field-2">Field 2</SelectItem>
                <SelectItem value="field-3">Field 3</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              onClick={() => toast.success("Filters reset")}
            >
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
              <p className="text-slate-900">{currentWeek[index].date}</p>
            </div>
            
            <Card className="p-4 min-h-[200px] space-y-2">
              {currentWeek[index].events.length === 0 ? (
                <p className="text-slate-400 text-center mt-8">No events</p>
              ) : (
                currentWeek[index].events.map((event, eventIdx) => (
                  <div
                    key={eventIdx}
                    className={`p-3 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-shadow ${
                      eventColors[event.type as keyof typeof eventColors]
                    }`}
                    onClick={() => setSelectedEvent({ ...event, date: currentWeek[index].date })}
                  >
                    <p className="mb-1">{event.field}</p>
                    <p className="text-slate-600">{event.time}</p>
                    {event.label && (
                      <Badge variant="destructive" className="mt-2">
                        {event.label}
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
              {selectedEvent.label && (
                <div>
                  <p className="text-slate-600 mb-1">Alert</p>
                  <Badge variant="destructive">{selectedEvent.label}</Badge>
                </div>
              )}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-slate-700">
                  Duration: 2 hours • Water volume: 15,000 liters • Fire risk impact: ↓ 14% reduction
                </p>
              </div>
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
