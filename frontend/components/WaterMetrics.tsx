/**
 * WaterMetrics component displays detailed water usage metrics and analytics.
 *
 * Shows water savings, usage trends, and detailed breakdowns by field and time period.
 *
 * @component
 * @returns {JSX.Element} The water metrics view
 */
import { useState, useCallback } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { MetricWidget } from "./MetricWidget";
import { Download, FileText, Mail, ChevronDown, ChevronUp } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { toast } from "sonner";

export function WaterMetrics(): JSX.Element {
  const [chartsExpanded, setChartsExpanded] = useState(true);
  const [tableExpanded, setTableExpanded] = useState(true);
  const heroMetrics = [
    {
      label: "Water Saved This Season",
      value: "230,000 liters",
      trend: "down" as const,
      trendValue: "vs. typical: ↓ 25%",
    },
    {
      label: "Cost Savings",
      value: "$575",
      trend: "up" as const,
      trendValue: "Cost reduction",
    },
    {
      label: "Fire Risk Reduction",
      value: "22%",
      trend: "down" as const,
      trendValue: "Improving",
    },
    {
      label: "Crop Health Score",
      value: "8.2/10",
      trend: "up" as const,
      trendValue: "Stable",
    },
  ];

  const agentPerformance = [
    {
      agent: "Fire-Adaptive Irrigation",
      recsSent: 24,
      accepted: 20,
      acceptRate: "83%",
      positiveOutcomes: 18,
      outcomeRate: "75%",
      avgConfidence: "87%",
    },
    {
      agent: "Water Efficiency",
      recsSent: 12,
      accepted: 11,
      acceptRate: "92%",
      positiveOutcomes: 11,
      outcomeRate: "100%",
      avgConfidence: "92%",
    },
    {
      agent: "PSPS Anticipation",
      recsSent: 3,
      accepted: 3,
      acceptRate: "100%",
      positiveOutcomes: 3,
      outcomeRate: "100%",
      avgConfidence: "95%",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2>Water & Fire Metrics Dashboard</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success("PDF report generated. Check your downloads.")}
          >
            <Download className="h-4 w-4 mr-2" />
            PDF Report
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success("CSV file exported successfully.")}
          >
            <FileText className="h-4 w-4 mr-2" />
            CSV Export
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success("Report emailed to john@sunnydalefarm.com")}
          >
            <Mail className="h-4 w-4 mr-2" />
            Email Report
          </Button>
        </div>
      </div>

      {/* Date Range Selector */}
      <div className="flex gap-2">
        <Select
          defaultValue="30-days"
          onValueChange={(value) => toast.info(`Viewing data for: ${value}`)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Select period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="30-days">Last 30 Days</SelectItem>
            <SelectItem value="q3">Q3 2024</SelectItem>
            <SelectItem value="year">This Year</SelectItem>
            <SelectItem value="custom">Custom Range</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {heroMetrics.map((metric, index) => (
          <MetricWidget key={index} {...metric} />
        ))}
      </div>

      {/* Charts - Collapsible Section */}
      <Collapsible open={chartsExpanded} onOpenChange={setChartsExpanded}>
        <Card className="p-6">
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between mb-4">
              <h3>Performance Charts</h3>
              {chartsExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="mb-4">Water Use Over Time</h3>
                <div className="h-64 bg-gradient-to-br from-emerald-50 to-blue-50 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <p className="text-slate-600 font-medium">Chart Placeholder</p>
                    <p className="text-slate-500 text-sm">
                      Area chart showing 6-month water usage trend
                    </p>
                    <p className="text-slate-400 text-xs mt-2">
                      Ready for Recharts integration
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="mb-4">Fire Risk Trajectory</h3>
                <div className="h-64 bg-gradient-to-br from-red-50 to-green-50 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <p className="text-slate-600 font-medium">Chart Placeholder</p>
                    <p className="text-slate-500 text-sm">
                      Line chart showing fire risk levels over 6 months
                    </p>
                    <p className="text-slate-400 text-xs mt-2">
                      Ready for Recharts integration
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="mb-4">Crop Health (NDVI) Trend</h3>
                <div className="h-64 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <p className="text-slate-600 font-medium">Chart Placeholder</p>
                    <p className="text-slate-500 text-sm">
                      Area chart showing NDVI values (0-1 scale)
                    </p>
                    <p className="text-slate-400 text-xs mt-2">
                      Ready for Recharts integration
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="mb-4">Drought Stress Index</h3>
                <div className="h-64 bg-gradient-to-br from-yellow-50 to-red-50 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <p className="text-slate-600 font-medium">Chart Placeholder</p>
                    <p className="text-slate-500 text-sm">
                      Bar chart showing weekly drought stress levels
                    </p>
                    <p className="text-slate-400 text-xs mt-2">
                      Ready for Recharts integration
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Agent Performance Table - Collapsible */}
      <Collapsible open={tableExpanded} onOpenChange={setTableExpanded}>
        <Card className="p-6">
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between mb-4">
              <h3>Agent Performance Summary</h3>
              {tableExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead className="text-right">Recs Sent</TableHead>
                  <TableHead className="text-right">Accepted</TableHead>
                  <TableHead className="text-right">Accept Rate</TableHead>
                  <TableHead className="text-right">Positive Outcomes</TableHead>
                  <TableHead className="text-right">Outcome Rate</TableHead>
                  <TableHead className="text-right">Avg Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {agentPerformance.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.agent}</TableCell>
                    <TableCell className="text-right">{row.recsSent}</TableCell>
                    <TableCell className="text-right">{row.accepted}</TableCell>
                    <TableCell className="text-right text-emerald-600">{row.acceptRate}</TableCell>
                    <TableCell className="text-right">{row.positiveOutcomes}</TableCell>
                    <TableCell className="text-right text-emerald-600">{row.outcomeRate}</TableCell>
                    <TableCell className="text-right">{row.avgConfidence}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  );
}
