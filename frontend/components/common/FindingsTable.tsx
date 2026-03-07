"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FileCode, ExternalLink, ShieldAlert } from "lucide-react";
import { Finding } from "@/shared/types/finding.type";

const FindingsTable = ({ findings, onOpen }: { findings: Finding[], onOpen: (f: Finding) => void }) => {
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
    <div className="space-y-4 w-full overflow-hidden">
      {/* Шапка таблицы */}
      <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 text-sm font-medium text-muted-foreground uppercase tracking-wider">
        <div className="col-span-4">Файл и строка</div>
        <div className="col-span-3">Тип секрета</div>
        <div className="col-span-2">Критичность</div>
        <div className="col-span-3">Найденное значение</div>
      </div>
      
      <div className="space-y-3 w-full">
        {findings.map((f, idx) => (
          <Card 
            key={f.id || idx} 
            className="group hover:border-primary/30 transition-all duration-300 cursor-pointer active:scale-[0.99] w-full overflow-hidden"
            onClick={() => onOpen(f)}
          >
            <CardContent className="p-4 md:px-6 w-full">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center w-full">
                
                {/* Файл и строка */}
                <div className="col-span-1 md:col-span-4 flex items-center gap-3 min-w-0">
                  <div className="p-2 shrink-0 rounded-lg bg-secondary/50 group-hover:bg-primary/10 transition-colors">
                    <FileCode className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-medium truncate" title={f.file_path}>
                      {f.file_path.split(/[\/\\]/).pop()} 
                      <span className="text-muted-foreground ml-2 text-xs">L:{f.line_number}</span>
                    </span>
                    <span className="text-xs text-muted-foreground truncate opacity-60" title={f.file_path}>
                      {f.file_path}
                    </span>
                  </div>
                </div>

                {/* Тип секрета */}
                <div className="col-span-1 md:col-span-3 flex items-center min-w-0">
                  <Badge variant="outline" className="font-mono text-[10px] tracking-tight truncate">
                    {f.secret_type}
                  </Badge>
                </div>

                {/* Критичность */}
                <div className="col-span-1 md:col-span-2 flex items-center shrink-0">
                  <Badge variant={getSeverityVariant(f.severity)} className="capitalize">
                    {f.severity}
                  </Badge>
                </div>

                {/* ЖЕСТКАЯ ЗАЩИТА: Значение и контекст кода */}
                <div className="col-span-1 md:col-span-3 flex flex-col min-w-0 w-full overflow-hidden">
                  <div className="text-xs font-mono font-bold text-destructive break-all line-clamp-1" title={f.matched_value}>
                    {f.matched_value}
                  </div>
                  {f.line_content && (
                    <div 
                      className="text-[10px] text-muted-foreground mt-1 break-all line-clamp-2 opacity-70 font-mono bg-muted/50 p-1 rounded w-full"
                      title={f.line_content}
                    >
                      {f.line_content}
                    </div>
                  )}
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