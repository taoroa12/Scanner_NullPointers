import axios from "./axios";

export async function exportReport(scan_id: string, format: "csv" | "json" = "json"): Promise<Blob> {
  const resp = await axios.get(`/api/scan/${encodeURIComponent(scan_id)}/export`, {
    params: { format },
    responseType: "blob",
  });
  return resp.data as Blob;
}