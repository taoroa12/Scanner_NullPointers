import { getScanReport } from "@/api/scan.api";
import SummaryDashboard from "@/components/common/SummaryDashboard";
import ReportContainer from "@/components/common/ReportContainer";
import { Shield, ChevronLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default async function ReportPage({ params }: { params: { id: string } }) {
  const { id } = await params;
  let report = null;
  let error = null;

  try {
    report = await getScanReport(id);
  } catch (e: any) {
    error = e.message;
  }

  return (
    <div className="min-h-[calc(100vh-64px)] bg-hero-gradient">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <Link href="/">
          <Button variant="ghost" className="mb-8 gap-2 -ml-4">
            <ChevronLeft className="w-4 h-4" />
            Назад к сканированию
          </Button>
        </Link>

        {error ? (
          <div className="flex flex-col items-center justify-center py-24 bg-card/20 rounded-2xl border border-dashed border-destructive/20">
            <Shield className="w-12 h-12 text-destructive/40 mb-4" />
            <h3 className="text-xl font-bold">Ошибка загрузки отчёта</h3>
            <p className="text-muted-foreground">{error}</p>
          </div>
        ) : report ? (
          <div className="space-y-12 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border/40 pb-8">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Shield className="w-6 h-6" />
                  </div>
                  <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
                    Отчёт о сканировании
                  </h1>
                </div>
                <p className="text-muted-foreground text-lg">
                  Проект: <span className="text-foreground font-medium">{report.project_name}</span>
                </p>
              </div>
              
              <div className="flex flex-col items-end gap-1 text-sm text-muted-foreground">
                <span>ID: {id}</span>
                <span>Дата: {new Date().toLocaleDateString('ru-RU')}</span>
              </div>
            </div>
            
            <section className="space-y-6">
              <h2 className="text-xl font-bold">Общая статистика</h2>
              <SummaryDashboard summary={report.summary} />
            </section>

            <section className="space-y-6">
              <h2 className="text-xl font-bold">Обнаруженные уязвимости</h2>
              <ReportContainer findings={report.findings} projectName={report.project_name} />
            </section>
          </div>
        ) : (
          <div className="flex items-center justify-center py-24">
            <p>Загрузка отчёта...</p>
          </div>
        )}
      </div>
    </div>
  );
}
