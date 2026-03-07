"use client";

import { useState, useMemo } from "react";
import { Finding } from "@/shared/types/finding.type";
import { Severity } from "@/shared/types/recommendation.type";
import FindingsTable from "./FindingsTable";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Download, Filter, Code, Info } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

interface ReportContainerProps {
  findings: Finding[];
  projectName: string;
}

const ReportContainer = ({ findings, projectName }: ReportContainerProps) => {
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const filteredFindings = useMemo(() => {
    if (severityFilter === "all") return findings;
    return findings.filter((f) => f.severity === severityFilter);
  }, [findings, severityFilter]);

  const downloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(findings, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `scan_report_${projectName}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const downloadCSV = () => {
    const headers = ["ID", "File Path", "Line Number", "Secret Type", "Severity", "Matched Value"];
    const csvContent = [
      headers.join(","),
      ...findings.map(f => [
        f.id.toString(),
        f.file_path,
        f.line_number.toString(),
        f.secret_type,
        f.severity,
        `"${f.matched_value.replace(/"/g, '""')}"`
      ].join(","))
    ].join("\n");

    const dataStr = "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `scan_report_${projectName}.csv`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const getSeverityVariant = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'warning';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-card/40 p-4 rounded-xl border border-border/40">
        <div className="flex items-center gap-3 cursor-pointer">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Фильтр:</span>
          
          <Select value={severityFilter} onValueChange={(val: any) => setSeverityFilter(val)}>
            <SelectTrigger className="w-[180px] cursor-pointer">
              <SelectValue placeholder="Все уровни" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все уровни</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={downloadJSON} className="gap-2 cursor-pointer">
            <Download className="w-4 h-4" />
            Скачать JSON
          </Button>
          <Button variant="outline" size="sm" onClick={downloadCSV} className="gap-2 cursor-pointer">
            <Download className="w-4 h-4" />
            Скачать CSV
          </Button>
        </div>
      </div>

      <FindingsTable findings={filteredFindings} onOpen={setSelectedFinding} />

      <Dialog open={!!selectedFinding} onOpenChange={() => setSelectedFinding(null)}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <Badge variant={selectedFinding ? getSeverityVariant(selectedFinding.severity) : 'outline'}>
                {selectedFinding?.severity}
              </Badge>
              <DialogTitle className="text-xl">Детали уязвимости</DialogTitle>
            </div>
            <DialogDescription className="font-mono text-xs break-all">
              {selectedFinding?.file_path}:{selectedFinding?.line_number}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-4">
            <section className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                <Code className="w-4 h-4" />
                <span>Фрагмент кода</span>
              </div>
              <div className="bg-zinc-950 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-zinc-800">
                <pre className="text-zinc-300">
                  <code>{selectedFinding?.line_content || "Контент недоступен"}</code>
                </pre>
              </div>
            </section>

            <section className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                <Info className="w-4 h-4" />
                <span>Рекомендация по устранению</span>
              </div>
              <div className="bg-secondary/30 rounded-lg p-4 space-y-3 border border-border/40">
                <p className="text-sm font-bold">{selectedFinding?.recommendation?.title}</p>
                
                <div className="space-y-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Проблема:</span>
                  <p className="text-sm text-foreground leading-relaxed">
                    {selectedFinding?.recommendation?.problem}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Решение:</span>
                  <p className="text-sm text-foreground leading-relaxed">
                    {selectedFinding?.recommendation?.solution}
                  </p>
                </div>

                {selectedFinding?.recommendation?.code_example && (
                  <div className="space-y-2 pt-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Пример исправления:</span>
                    <div className="bg-zinc-950 rounded-lg p-3 font-mono text-xs overflow-x-auto border border-zinc-800">
                      <pre className="text-emerald-400">
                        <code>{selectedFinding?.recommendation?.code_example}</code>
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </section>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ReportContainer;
