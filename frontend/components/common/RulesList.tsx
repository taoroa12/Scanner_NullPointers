"use client";
import { useEffect, useState, useMemo } from "react";
import { getRules, deleteRule } from "@/api/rules.api";
import RuleFormModal from "./modals/RuleFormModal";
import { Button } from "../ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trash2, Plus, Code, Search, Loader2, Info, ArrowUpDown } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RuleResponse } from "@/shared/types/rule.types";

export default function RulesList() {
  const [rules, setRules] = useState<RuleResponse[]>([]);
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedRule, setSelectedRule] = useState<RuleResponse | null>(null);
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const r = await getRules();
      setRules(r);
    } catch (e: any) {
      alert("Не удалось загрузить правила: " + (e?.message ?? ""));
    } finally {
      setLoading(false);
    }
  }

  const sortedRules = useMemo(() => {
    const severityMap: Record<string, number> = {
      critical: 4,
      high: 3,
      medium: 2,
      low: 1
    };

    return [...rules].sort((a, b) => {
      const weightA = severityMap[a.severity.toLowerCase()] || 0;
      const weightB = severityMap[b.severity.toLowerCase()] || 0;
      return sortOrder === "desc" ? weightB - weightA : weightA - weightB;
    });
  }, [rules, sortOrder]);

  async function onDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    if (!confirm("Удалить правило?")) return;
    try {
      await deleteRule(id);
      setRules(prev => prev.filter(x => x.id !== id));
    } catch (e: any) {
      alert("Ошибка при удалении: " + (e?.message ?? ""));
    }
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
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-xl font-bold">Активные правила ({rules.length})</h2>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-secondary/30 px-3 py-1.5 rounded-lg border border-border/20">
            <ArrowUpDown className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Уровень угрозы:</span>
            <Select value={sortOrder} onValueChange={(val: any) => setSortOrder(val)}>
              <SelectTrigger className="h-7 w-[110px] text-xs bg-transparent border-none shadow-none focus:ring-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">По убыванию</SelectItem>
                <SelectItem value="asc">По возрастанию</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button onClick={() => setShow(true)} className="gap-2 cursor-pointer h-9 px-4">
            <Plus className="w-4 h-4" />
            Добавить правило
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading && (
          <div className="col-span-full flex flex-col items-center justify-center py-24 text-muted-foreground">
            <Loader2 className="w-8 h-8 animate-spin mb-4" />
            <p>Загрузка базы правил...</p>
          </div>
        )}
        
        {!loading && rules.length === 0 && (
          <div className="col-span-full flex flex-col items-center justify-center py-24 bg-card/20 rounded-2xl border border-dashed border-border/40">
            <Code className="w-12 h-12 text-muted-foreground/40 mb-4" />
            <h3 className="text-lg font-medium">Правила отсутствуют</h3>
            <p className="text-sm text-muted-foreground">Добавьте свое первое правило для начала сканирования.</p>
          </div>
        )}

        {sortedRules.map(r => (
          <Card 
            key={r.id} 
            className="group hover:border-primary/30 transition-all duration-300 cursor-pointer active:scale-[0.99]"
            onClick={() => setSelectedRule(r)}
          >
            <CardContent className="p-5">
              <div className="flex justify-between items-start gap-4">
                <div className="space-y-3 min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-foreground truncate">{r.name}</span>
                    <Badge variant={getSeverityVariant(r.severity)} className="text-[10px] h-5 px-1.5">
                      {r.severity}
                    </Badge>
                  </div>
                  
                  <div className="flex items-start gap-2 bg-secondary/30 p-2.5 rounded-lg border border-border/20">
                    <Code className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                    <code className="text-xs font-mono text-muted-foreground break-all line-clamp-2">
                      {r.pattern}
                    </code>
                  </div>
                </div>

                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={(e) => onDelete(e, r.id)}
                  className="text-muted-foreground cursor-pointer hover:text-destructive hover:bg-destructive/10 transition-colors shrink-0"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!selectedRule} onOpenChange={() => setSelectedRule(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <Badge variant={selectedRule ? getSeverityVariant(selectedRule.severity) : 'outline'}>
                {selectedRule?.severity}
              </Badge>
              <DialogTitle className="text-xl">Детали правила: {selectedRule?.name}</DialogTitle>
            </div>
            <DialogDescription className="font-mono text-xs">
              ID: {selectedRule?.id} | {selectedRule?.is_custom ? 'Пользовательское' : 'Системное'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-4">
            <section className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                <Code className="w-4 h-4" />
                <span>Регулярное выражение (Pattern)</span>
              </div>
              <div className="bg-zinc-950 rounded-lg p-4 font-mono text-sm overflow-x-auto border border-zinc-800">
                <pre className="text-zinc-300">
                  <code>{selectedRule?.pattern}</code>
                </pre>
              </div>
            </section>

            <section className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                <Info className="w-4 h-4" />
                <span>Описание и рекомендации</span>
              </div>
              <div className="bg-secondary/30 rounded-lg p-4 space-y-4 border border-border/40">
                {selectedRule?.description && (
                  <div className="space-y-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Описание:</span>
                    <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                      {selectedRule.description}
                    </p>
                  </div>
                )}
                
                {selectedRule?.recommendation ? (
                  <div className="space-y-1 pt-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Рекомендация по исправлению:</span>
                    <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                      {selectedRule.recommendation}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground italic">Рекомендации для данного правила отсутствуют.</p>
                )}
              </div>
            </section>
          </div>
        </DialogContent>
      </Dialog>

      <RuleFormModal 
        open={show} 
        onClose={() => setShow(false)} 
        onSuccess={load}
      />
    </div>
  );
}
