import { type ScanResult } from "@/shared/types/scan.types";
import axios from "./axios";

export async function uploadAndScan(file: File): Promise<{ scan_id: string; status: string; findings_count: number }> {
  const fd = new FormData();
  fd.append("file", file);

  const resp = await axios.post("/api/scan/", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data;
}

export async function getScanReport(scan_id: string): Promise<ScanResult> {
  const resp = await axios.get<ScanResult>(`/api/scan/${encodeURIComponent(scan_id)}`);
  return resp.data;
}

export async function scanGithubRepo(repoUrl: string): Promise<{ scan_id: string; status: string; findings_count: number }> {
  const resp = await axios.post("/api/scan/github", { repo_url: repoUrl });
  return resp.data;
}