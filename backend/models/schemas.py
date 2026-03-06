from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class Recommendation(BaseModel):
    title: str
    problem: str
    solution: str
    code_example: str

class Finding(BaseModel):
    id: int
    file_path: str
    line_number: int
    secret_type: str
    severity: str  # critical, high, medium, low
    matched_value: str
    recommendation: Recommendation

class ScanSummary(BaseModel):
    total_files_scanned: int
    total_findings: int
    by_severity: Dict[str, int]

class ScanResult(BaseModel):
    # Разрешаем использовать произвольные типы, если потребуется
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    scan_id: str
    status: str
    project_name: str
    summary: ScanSummary
    findings: List[Finding]