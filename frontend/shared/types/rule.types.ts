import { type Severity } from "./recommendation.type";

export interface RuleResponse {
  id: string;
  name: string;
  pattern: string;
  severity: Severity;
  is_custom: boolean;
  description?: string;
  recommendation?: string;
}

export interface RuleCreate {
  name: string;
  pattern: string;
  severity: Severity;
}