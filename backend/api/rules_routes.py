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
    """Возвращает все активные правила (системные + кастомные)"""
    all_rules = rules_manager.get_enabled_rules()
    rules_response = []
    
    for rule in all_rules:
        # Конвертируем RiskLevel в severity
        severity_map = {
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        
        # Специфичный маппинг для некоторых системных правил
        severity = severity_map.get(rule.risk_level.value, "medium")
        if rule.name == "AWS Access Key ID":
            severity = "critical"
        
        rules_response.append(RuleResponse(
            id=rule.id,
            name=rule.name,
            pattern=rule.pattern,
            severity=severity,
            is_custom=rule.is_custom
        ))
    
    return rules_response

@router.post("/", response_model=RuleResponse)
async def add_custom_rule(rule_data: RuleCreate):
    """Добавляет пользовательское правило и сохраняет его в YAML"""
    if not rules_manager.validate_pattern(rule_data.pattern):
        raise HTTPException(status_code=400, detail="Invalid Regex pattern")
    
    new_rule = rules_manager.add_custom_rule(
        name=rule_data.name,
        pattern=rule_data.pattern,
        severity=rule_data.severity
    )
    
    return RuleResponse(
        id=new_rule.id,
        name=new_rule.name,
        pattern=new_rule.pattern,
        severity=rule_data.severity,
        is_custom=True
    )

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    """Удаляет пользовательское правило"""
    if rule_id.startswith("sys-"):
        raise HTTPException(status_code=400, detail="Cannot delete system rules")
    
    success = rules_manager.delete_custom_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found or already deleted")
    
    return {"status": "deleted", "id": rule_id}