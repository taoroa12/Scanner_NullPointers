"use client";

import { useState, useRef } from "react";
import { UploadCloud, FileArchive, Loader2 } from "lucide-react";
import { uploadAndScan } from "@/api/scan.api";
import { cn } from "@/lib/utils";

const FileUploader = ({ onUploaded }: { onUploaded: (scanId: string, findingsCount?: number) => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleUpload(selectedFile: File) {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const data = await uploadAndScan(selectedFile);
      onUploaded(data.scan_id, data.findings_count);
    } catch (e: any) {
      alert("Ошибка при загрузке: " + (e?.message ?? "неизвестная ошибка"));
    } finally {
      setLoading(false);
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.zip')) {
        setFile(droppedFile);
        handleUpload(droppedFile);
      } else {
        alert("Пожалуйста, загрузите ZIP-архив");
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      handleUpload(selectedFile);
    }
  };

  return (
    <div 
      className={cn(
        "relative w-full max-w-3xl mx-auto mt-8 group transition-all duration-300",
        dragActive ? "scale-[1.02]" : "scale-100"
      )}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        onChange={handleChange}
        className="hidden"
      />
      
      <div 
        onClick={() => inputRef.current?.click()}
        className={cn(
          "flex flex-col items-center justify-center w-full h-64 rounded-2xl border-2 border-dashed transition-all cursor-pointer",
          dragActive 
            ? "border-primary bg-primary/5 shadow-[0_0_30px_rgba(var(--primary),0.1)]" 
            : "border-border/60 bg-card/20 hover:border-primary/50 hover:bg-card/40"
        )}
      >
        <div className="flex flex-col items-center justify-center pt-5 pb-6">
          <div className={cn(
            "p-4 rounded-2xl bg-secondary/50 mb-4 transition-transform group-hover:scale-110",
            loading && "animate-pulse"
          )}>
            {loading ? (
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            ) : file ? (
              <FileArchive className="w-8 h-8 text-primary" />
            ) : (
              <UploadCloud className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
            )}
          </div>
          
          <p className="mb-2 text-lg font-medium text-foreground tracking-tight">
            {loading ? "Идет сканирование..." : file ? file.name : "Перетащите ZIP-архив сюда"}
          </p>
          <p className="text-sm text-muted-foreground">
            или нажмите для выбора файла
          </p>
        </div>
      </div>

      {loading && (
        <div className="absolute inset-0 bg-background/20 backdrop-blur-[1px] rounded-2xl flex items-center justify-center" />
      )}
    </div>
  );
}

export default FileUploader;
