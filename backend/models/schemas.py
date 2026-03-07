# models/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

# === Enums ===
class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SecretType(str, Enum):
    API_KEY = "api_key"        # было API_KEY = "API_KEY"
    TOKEN = "token"             # было TOKEN = "TOKEN"  
    PRIVATE_KEY = "private_key" # было PRIVATE_KEY = "PRIVATE_KEY"
    PASSWORD = "password"       # было PASSWORD = "PASSWORD"
    AWS_KEY = "aws_key"         # было AWS_KEY = "AWS_KEY"
    GENERIC = "generic"         # было GENERIC = "GENERIC"

# === Rule ===
class Rule(BaseModel):
    """Правило для поиска секретов"""
    id: Optional[str] = Field(None, description="ID правила")
    name: str = Field(..., description="Название правила")
    pattern: str = Field(..., description="Регулярное выражение")
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Уровень риска")
    secret_type: SecretType = Field(SecretType.GENERIC, description="Тип секрета")
    description: Optional[str] = Field(None, description="Описание")
    recommendation: Optional[str] = Field(None, description="Рекомендация")
    enabled: bool = Field(True, description="Активно/неактивно")
    entropy_threshold: Optional[float] = Field(None, description="Порог энтропии")
    is_custom: bool = Field(False, description="Пользовательское ли правило")

# === Recommendation ===
class Recommendation(BaseModel):
    title: str
    problem: str
    solution: str
    code_example: str

# === Finding ===
class Finding(BaseModel):
    """Результат поиска секрета"""
    id: int
    file_path: str
    line_number: int
    secret_type: str
    severity: str
    matched_value: str
    recommendation: Recommendation
    entropy: Optional[float] = None
    encoding_type: Optional[str] = None
    rule_name: Optional[str] = None
    line_content: Optional[str] = None

# === ScanSummary ===
class ScanSummary(BaseModel):
    total_files_scanned: int
    total_findings: int
    by_severity: Dict[str, int]

# === ScanResult ===
class ScanResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    scan_id: str
    status: str
    project_name: str
    summary: ScanSummary
    findings: List[Finding]

# === Request Models ===
class RepoScanRequest(BaseModel):
    repo_url: str = Field(..., description="Ссылка на публичный GitHub репозиторий")