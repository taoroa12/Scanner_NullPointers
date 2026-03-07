"use client";

import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle, AlertTriangle, ShieldCheck, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

const SummaryDashboard = ({ summary }: { summary: any }) => {
  const stats = [
    {
      label: "Critical",
      value: summary?.by_severity?.critical ?? 0,
      icon: ShieldAlert,
      color: "text-red-500",
      bg: "bg-red-500/10",
      border: "border-red-500/20"
    },
    {
      label: "High",
      value: summary?.by_severity?.high ?? 0,
      icon: AlertCircle,
      color: "text-orange-500",
      bg: "bg-orange-500/10",
      border: "border-orange-500/20"
    },
    {
      label: "Medium",
      value: summary?.by_severity?.medium ?? 0,
      icon: AlertTriangle,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20"
    },
    {
      label: "Low",
      value: summary?.by_severity?.low ?? 0,
      icon: ShieldCheck,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} className={cn("border-2 transition-all hover:scale-[1.02]", stat.border)}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  {stat.label}
                </p>
                <p className={cn("text-3xl font-bold mt-1", stat.color)}>
                  {stat.value}
                </p>
              </div>
              <div className={cn("p-3 rounded-xl", stat.bg)}>
                <stat.icon className={cn("w-6 h-6", stat.color)} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default SummaryDashboard;
