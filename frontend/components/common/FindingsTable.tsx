"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FileCode, ExternalLink, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

const FindingsTable = ({ findings, onOpen }: { findings: any[], onOpen: (f: any) => void }) => {
  if (!findings || findings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-card/20 rounded-2xl border border-dashed border-border/40">
        <ShieldAlert className="w-12 h-12 text-muted-foreground/40 mb-4" />
        <h3 className="text-lg font-medium text-muted-foreground">Утечек не обнаружено</h3>
        <p className="text-sm text-muted-foreground/60">Ваш проект кажется безопасным</p>
      </div>
    );
  }

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
    <div className="space-y-4">
      <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 text-sm font-medium text-muted-foreground uppercase tracking-wider">
        <div className="col-span-5">Файл</div>
        <div className="col-span-1">Строка</div>
        <div className="col-span-3">Тип секрета</div>
        <div className="col-span-2">Критичность</div>
        <div className="col-span-1"></div>
      </div>
      
      <div className="space-y-3">
        {findings.map((f, idx) => (
          <Card key={f.id || idx} className="group hover:border-primary/30 transition-all duration-300">
            <CardContent className="p-4 md:px-6">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                {/* File Path */}
                <div className="col-span-1 md:col-span-5 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-secondary/50 group-hover:bg-primary/10 transition-colors">
                    <FileCode className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-medium truncate" title={f.file_path}>
                      {f.file_path.split('/').pop()}
                    </span>
                    <span className="text-xs text-muted-foreground truncate opacity-60">
                      {f.file_path}
                    </span>
                  </div>
                </div>

                {/* Line Number */}
                <div className="col-span-1 md:col-span-1 flex md:justify-start items-center">
                  <span className="text-sm font-mono text-muted-foreground">
                    L:{f.line_number}
                  </span>
                </div>

                {/* Secret Type */}
                <div className="col-span-1 md:col-span-3 flex items-center">
                  <Badge variant="outline" className="font-mono text-[10px] tracking-tight">
                    {f.secret_type}
                  </Badge>
                </div>

                {/* Severity */}
                <div className="col-span-1 md:col-span-2 flex items-center">
                  <Badge variant={getSeverityVariant(f.severity)} className="capitalize">
                    {f.severity}
                  </Badge>
                </div>

                {/* Action */}
                <div className="col-span-1 md:col-span-1 flex justify-end">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={() => onOpen(f)}
                    className="h-8 w-8 hover:bg-primary/10 hover:text-primary transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default FindingsTable;
