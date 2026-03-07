export type Severity = "critical" | "high" | "medium" | "low";

export interface Recommendation {
  title: string;
  problem: string;
  solution: string;
  code_example: string;
}