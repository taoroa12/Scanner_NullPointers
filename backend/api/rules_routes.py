from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import uuid
import re

from services.rules_manager import RulesManager

router = APIRouter(prefix="/api/rules", tags=["Rules"])
rules_manager = RulesManager()

class RuleResponse(BaseModel):
    id: str
    name: str
    pattern: str
    severity: str
    is_custom: bool

class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    pattern: str = Field(..., min_length=1)
    severity: Literal["critical", "high", "medium", "low"]

@router.get("/", response_model=List[RuleResponse])
async def get_all_rules():
    """Возвращает все активные правила из YAML"""
    yaml_rules = rules_manager.get_enabled_rules()
    rules_response = []
    
    for i, rule in enumerate(yaml_rules, start=1):
        # Конвертируем RiskLevel в severity
        severity_map = {
            "high": "critical" if rule.name == "AWS Access Key ID" else "high",
            "medium": "medium",
            "low": "low"
        }
        
        rules_response.append(RuleResponse(
            id=f"sys-{i}",
            name=rule.name,
            pattern=rule.pattern,
            severity=severity_map.get(rule.risk_level.value, "medium"),
            is_custom=False
        ))
    
    return rules_response

@router.post("/", response_model=RuleResponse)
async def add_custom_rule(rule_data: RuleCreate):
    """Добавляет пользовательское правило (моковое сохранение для фронтенда)"""
    try:
        re.compile(rule_data.pattern)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid Regex pattern")
    
    new_rule = RuleResponse(
        id=f"cust-{str(uuid.uuid4())[:6]}",
        name=rule_data.name,
        pattern=rule_data.pattern,
        severity=rule_data.severity,
        is_custom=True
    )
    return new_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    """Удаляет правило (только кастомные)"""
    if rule_id.startswith("sys-"):
        raise HTTPException(status_code=400, detail="Cannot delete system rules")
    
    return {"status": "deleted", "id": rule_id}