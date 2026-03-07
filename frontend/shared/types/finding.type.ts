import { type Recommendation, type Severity } from "./recommendation.type";

export interface Finding {
  id: number;
  file_path: string;
  line_number: number;
  secret_type: string;
  severity: Severity;
  matched_value: string;
  recommendation: Recommendation;
  entropy?: number | null;
  encoding_type?: string | null;
  rule_name?: string;
  line_content?: string;
}