"use client";
import { useState } from "react";
import FileUploader from "@/components/common/FileUploader";
import GithubScanner from "@/components/common/GithubScanner";
import ReportContainer from "@/components/common/ReportContainer";
import { getScanReport } from "@/api/scan.api";
import SummaryDashboard from "@/components/common/SummaryDashboard";
import { Shield, Zap, Lock, Search, FolderArchive, Github } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { type ScanResult } from "@/shared/types/scan.types";

export default function ScanPage() {
  const [report, setReport] = useState<ScanResult | null>(null);

  async function onUploaded(scanId: string) {
    try {
      const r = await getScanReport(scanId);
      setReport(r);
    } catch {
      alert("Не удалось получить отчёт");
    }
  }

  return (
    <div className="min-h-[calc(100vh-64px)] bg-hero-gradient">
      <div className="max-w-7xl mx-auto px-6 py-16 md:py-24">
        {!report ? (
          <div className="flex flex-col items-center text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="relative group">
              <div className="absolute -inset-1 bg-linear-to-r from-primary/50 to-primary rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
              <div className="relative p-6 rounded-2xl bg-card border border-border/40 glow-primary">
                <Shield className="w-12 h-12 text-primary" />
              </div>
            </div>

            <div className="space-y-4 max-w-2xl">
              <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-foreground">
                Secret Scanner
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed">
                Обнаружение утечек API-ключей, токенов, паролей и приватных ключей в исходном коде
              </p>
            </div>

            <div className="w-full max-w-3xl space-y-12 animate-in fade-in slide-in-from-bottom-6 duration-1000">
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2 text-foreground/80 mb-2">
                  <FolderArchive className="w-5 h-5" />
                  <h2 className="text-xl font-bold">Локальный архив</h2>
                </div>
                <FileUploader onUploaded={(id) => onUploaded(id)} />
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/40" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-4 text-muted-foreground/60 font-medium tracking-widest">или через GitHub</span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2 text-foreground/80 mb-2">
                  <Github className="w-5 h-5" />
                  <h2 className="text-xl font-bold">Публичный репозиторий</h2>
                </div>
                <GithubScanner onUploaded={(id) => onUploaded(id)} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mt-16">
              <Card className="border-border/20 bg-card/20 hover:bg-card/40 transition-colors">
                <CardContent className="pt-6 flex flex-col items-center text-center space-y-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Search className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-lg">20+ паттернов</h3>
                  <p className="text-sm text-muted-foreground">
                    AWS, GitHub, Google, Slack, JWT и другие сервисы
                  </p>
                </CardContent>
              </Card>

              <Card className="border-border/20 bg-card/20 hover:bg-card/40 transition-colors">
                <CardContent className="pt-6 flex flex-col items-center text-center space-y-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Zap className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-lg">Энтропийный анализ</h3>
                  <p className="text-sm text-muted-foreground">
                    Обнаружение высокоэнтропийных строк и паролей
                  </p>
                </CardContent>
              </Card>

              <Card className="border-border/20 bg-card/20 hover:bg-card/40 transition-colors">
                <CardContent className="pt-6 flex flex-col items-center text-center space-y-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Lock className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-lg">100% локально</h3>
                  <p className="text-sm text-muted-foreground">
                    Данные обрабатываются на сервере и не покидают вашу сеть
                  </p>
                </CardContent>
              </Card>
            </div>

            <p className="text-xs text-muted-foreground/60 max-w-3xl leading-relaxed">
              Поддерживаемые файлы: .py, .js, .ts, .jsx, .tsx, .yaml, .yml, .env, .json, .xml, .sh, .cfg, .ini, .toml, .tf, .properties, .gradle, .rb, .go, .java, .php
            </p>
          </div>
        ) : (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between border-b border-border/40 pb-6">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">
                  Результат сканирования
                </h2>
                <p className="text-muted-foreground mt-1">
                  Проект: <span className="text-foreground font-medium">{report.project_name}</span>
                </p>
              </div>
              <button 
                onClick={() => setReport(null)}
                className="text-sm font-medium text-primary hover:underline"
              >
                Сканировать другой проект
              </button>
            </div>
            
            <SummaryDashboard summary={report.summary} />
            <ReportContainer findings={report.findings} projectName={report.project_name} />
          </div>
        )}
      </div>
    </div>
  );
}
