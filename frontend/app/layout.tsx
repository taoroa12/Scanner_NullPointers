import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { Shield, BookOpen, Scan } from "lucide-react";
import { Button } from "@/components/ui/button";
import { type ReactNode } from "react";

export const metadata: Metadata = {
  title: "Secret Scanner",
  description: "Обнаружение утечек API-ключей, токенов, паролей и приватных ключей в исходном коде",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="ru" className="dark">
      <body className="antialiased">
        <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg border border-primary/20 bg-primary/5">
                <Shield className="w-5 h-5 text-primary" />
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="font-bold tracking-tight text-lg">Secret Scanner</span>
                <span className="text-xs font-medium text-muted-foreground">v1.0</span>
              </div>
            </div>
            
            <nav className="flex items-center gap-1">
              <Link href="/">
                <Button variant="ghost" className="gap-2 h-9 cursor-pointer">
                  <Scan className="w-4 h-4" />
                  <span className="hidden sm:inline">Сканирование</span>
                </Button>
              </Link>
              <Link href="/rules">
                <Button variant="ghost" className="gap-2 h-9 cursor-pointer text-muted-foreground hover:text-foreground">
                  <BookOpen className="w-4 h-4" />
                  <span className="hidden sm:inline">Правила</span>
                </Button>
              </Link>
            </nav>
          </div>
        </header>
        <main className="relative">{children}</main>
      </body>
    </html>
  );
}
