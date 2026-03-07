"use client";
import React, { useState } from "react";
import { Github, Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { scanGithubRepo } from "@/api/scan.api";

interface GithubScannerProps {
  onUploaded: (scanId: string) => void;
}

const GithubScanner: React.FC<GithubScannerProps> = ({ onUploaded }) => {
  const [repoUrl, setRepoUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!repoUrl.trim()) {
      setError("Пожалуйста, введите URL репозитория");
      return;
    }

    if (!repoUrl.startsWith("https://github.com/")) {
      setError("Поддерживаются только ссылки на GitHub");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await scanGithubRepo(repoUrl.trim());
      onUploaded(result.scan_id);
    } catch (err: any) {
      console.error("GitHub scan error:", err);
      const detail =
        err.response?.data?.detail || "Ошибка при сканировании репозитория";
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto space-y-4">
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-linear-to-r from-primary/50 to-primary rounded-xl blur opacity-20 group-focus-within:opacity-40 transition duration-500"></div>
        <div className="relative flex items-center space-x-2 bg-card border border-border/40 rounded-xl p-1.5 pl-4 shadow-lg transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/20">
          <Github className="w-5 h-5 text-muted-foreground" />
          <Input
            type="text"
            placeholder="https://github.com/user/repo"
            value={repoUrl}
            onChange={(e) => {
              setRepoUrl(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={(e) => e.key === "Enter" && handleScan()}
            className="flex-1 bg-transparent border-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm h-9 px-2"
            disabled={isLoading}
          />
          <Button
            onClick={handleScan}
            disabled={isLoading}
            size="sm"
            className="rounded-lg px-6 cursor-pointer font-medium transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Сканирование...
              </>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                Проверить
              </>
            )}
          </Button>
        </div>
      </div>
      {error && (
        <p className="text-xs text-destructive text-center animate-in fade-in slide-in-from-top-1 duration-300">
          {error}
        </p>
      )}
    </div>
  );
};

export default GithubScanner;
