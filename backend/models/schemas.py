from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SecretType(str, Enum):
    API_KEY = "api_key"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    PASSWORD = "password"
    AWS_KEY = "aws_key"
    GENERIC = "generic"


class Rule(BaseModel):
    """Правило для поиска секретов"""
    name: str = Field(..., description="Название правила")
    pattern: str = Field(..., description="Регулярное выражение")
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Уровень риска")
    secret_type: SecretType = Field(SecretType.GENERIC, description="Тип секрета")
    description: Optional[str] = Field(None, description="Описание")
    enabled: bool = Field(True, description="Активно/неактивно")
    entropy_threshold: Optional[float] = Field(None, description="Порог энтропии")


class Recommendation(BaseModel):
    title: str
    problem: str
    solution: str
    code_example: str

class Finding(BaseModel):
    """Результат поиска секрета"""
    id: int
    file_path: str
    line_number: int
    secret_type: str  # Название правила
    severity: str  # critical, high, medium, low
    matched_value: str  # Замаскированный секрет
    recommendation: Recommendation
    # Дополнительные поля для внутреннего использования
    entropy: Optional[float] = None
    encoding_type: Optional[str] = None
    rule_name: Optional[str] = None
    line_content: Optional[str] = None


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