import type { RuleCreate, RuleResponse } from "@/shared/types/rule.types";
import axios from "./axios";

export async function getRules(): Promise<RuleResponse[]> {
  const response = await axios.get<RuleResponse[]>("/api/rules/");
  return response.data;
}

export async function addRule(data: RuleCreate): Promise<RuleResponse> {
  const response = await axios.post<RuleResponse>("/api/rules/", data);
  return response.data;
}

export async function deleteRule(id: string): Promise<{ status: string; id: string }> {
  const response = await axios.delete<{ status: string; id: string }>(`/api/rules/${encodeURIComponent(id)}`);
  return response.data;
}