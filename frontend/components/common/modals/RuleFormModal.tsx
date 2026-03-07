"use client";

import { type ReactNode, useState } from "react";
import { addRule } from "@/api/rules.api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription
} from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";
import { Select } from "@/components/ui/select";

const CustomLabel = ({ children, className }: { children: ReactNode, className?: string }) => (
  <label className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}>
    {children}
  </label>
);

export default function RuleFormModal({ open, onClose, onSuccess }: { open: boolean, onClose: () => void, onSuccess: () => void }) {
  const [name, setName] = useState("");
  const [pattern, setPattern] = useState("");
  const [severity, setSeverity] = useState<"critical" | "high" | "medium" | "low">("high");
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!name || !pattern) {
      alert("Пожалуйста, заполните все поля");
      return;
    }
    
    setLoading(true);
    try {
      await addRule({ name, pattern, severity });
      setName("");
      setPattern("");
      setSeverity("high");
      onSuccess();
      onClose();
    } catch (e: any) {
      alert("Ошибка: " + e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(val) => !val && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Добавить новое правило</DialogTitle>
          <DialogDescription>
            Создайте новое правило для поиска чувствительных данных с использованием регулярных выражений.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-6 py-4">
          <div className="grid gap-2">
            <CustomLabel>Название правила</CustomLabel>
            <Input 
              placeholder="Например: AWS Access Key" 
              value={name} 
              onChange={e => setName(e.target.value)}
              className="bg-secondary/20"
            />
          </div>
          
          <div className="grid gap-2">
            <CustomLabel>Регулярное выражение (Regex)</CustomLabel>
            <Input 
              placeholder="AKIA[0-9A-Z]{16}" 
              value={pattern} 
              onChange={e => setPattern(e.target.value)}
              className="font-mono text-sm bg-secondary/20"
            />
          </div>
          
          <div className="grid gap-2">
            <CustomLabel>Уровень критичности</CustomLabel>
            <select
              value={severity} 
              onChange={e => setSeverity(e.target.value as any)}
              className="flex h-10 w-full rounded-md border border-input bg-secondary/20 px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              
              <option value="critical" className="bg-card">Critical</option>
              <option value="high" className="bg-card">High</option>
              <option value="medium" className="bg-card">Medium</option>
              <option value="low" className="bg-card">Low</option>
            </select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose} disabled={loading}>
            Отмена
          </Button>
          <Button onClick={submit} disabled={loading} className="gap-2">
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? "Добавление..." : "Сохранить правило"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
