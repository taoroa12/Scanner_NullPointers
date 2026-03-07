import RulesList from "@/components/common/RulesList";
import { BookOpen, ShieldCheck } from "lucide-react";

export default function RulesPage() {
  return (
    <div className="min-h-[calc(100vh-64px)] bg-hero-gradient">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary">
                <BookOpen className="w-6 h-6" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
                База правил сканирования
              </h1>
            </div>
            <p className="text-muted-foreground text-lg max-w-2xl">
              Список паттернов и алгоритмов, используемых для обнаружения чувствительных данных в вашем коде.
            </p>
          </div>
          
          <div className="flex items-center gap-4 p-4 rounded-2xl bg-card border border-border/40 glow-primary md:max-w-xs">
            <ShieldCheck className="w-10 h-10 text-primary shrink-0" />
            <div className="text-sm">
              <p className="font-bold text-foreground">Безопасность прежде всего</p>
              <p className="text-muted-foreground">Все проверки выполняются на лету без сохранения данных.</p>
            </div>
          </div>
        </div>

        <RulesList />
      </div>
    </div>
  );
}
