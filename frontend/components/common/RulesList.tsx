"use client";
import { useEffect, useState } from "react";
import { getRules, deleteRule } from "@/api/rules.api";
import RuleFormModal from "./modals/RuleFormModal";
import { Button } from "../ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trash2, Plus, Code, Search, Loader2 } from "lucide-react";

export default function RulesList() {
  const [rules, setRules] = useState<any[]>([]);
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

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

  async function onDelete(id: string) {
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-xl font-bold">Активные правила ({rules.length})</h2>
        </div>
        <Button onClick={() => setShow(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Добавить правило
        </Button>
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

        {rules.map(r => (
          <Card key={r.id} className="group hover:border-primary/30 transition-all duration-300">
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
                  onClick={() => onDelete(r.id)}
                  className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors shrink-0"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <RuleFormModal 
        open={show} 
        onClose={() => setShow(false)} 
        onSuccess={load}
      />
    </div>
  );
}
