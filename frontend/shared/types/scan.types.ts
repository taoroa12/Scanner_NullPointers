import { type Finding } from "./finding.type";
import { type Severity } from "./recommendation.type";

export interface ScanSummary {
  total_files_scanned: number;
  total_findings: number;
  by_severity: Record<Severity, number>;
}

export interface ScanResult {
  scan_id: string;
  status: string;
  project_name: string;
  summary: ScanSummary;
  findings: Finding[];
}