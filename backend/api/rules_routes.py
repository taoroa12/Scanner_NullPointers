from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
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
    description: Optional[str] = None
    recommendation: Optional[str] = None

class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    pattern: str = Field(..., min_length=1)
    severity: Literal["critical", "high", "medium", "low"]

@router.get("/", response_model=List[RuleResponse])
async def get_all_rules():
    """Возвращает все активные правила (Системные + Кастомные из YAML)"""
    # Обновляем кастомные правила с диска перед выдачей
    rules_manager.load_custom_rules()
    all_rules = rules_manager.get_enabled_rules()
    
    rules_response = []
    
    for rule in all_rules:
        # Конвертируем RiskLevel (enum) в строку severity для фронтенда
        severity_map = {
            "high": "critical" if rule.name == "AWS Access Key ID" else "high",
            "medium": "medium",
            "low": "low"
        }
        
        rules_response.append(RuleResponse(
            id=rule.id,  # Теперь берем настоящий ID прямо из менеджера!
            name=rule.name,
            pattern=rule.pattern,
            severity=severity_map.get(rule.risk_level.value, "medium"),
            is_custom=rule.is_custom, # Берем флаг прямо из менеджера
            description=rule.description,
            recommendation=rule.recommendation
        ))
    
    return rules_response

@router.post("/", response_model=RuleResponse)
async def add_custom_rule(rule_data: RuleCreate):
    """Добавляет пользовательское правило и сохраняет в custom_rules.yaml"""
    try:
        re.compile(rule_data.pattern)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid Regex pattern")
    
    # Вызываем правильную функцию из вашего нового RulesManager
    new_rule = rules_manager.add_custom_rule(
        name=rule_data.name,
        pattern=rule_data.pattern,
        severity=rule_data.severity
    )
    
    # Формируем ответ для фронтенда
    severity_map = {"high": "high", "medium": "medium", "low": "low"}
    
    return RuleResponse(
        id=new_rule.id,
        name=new_rule.name,
        pattern=new_rule.pattern,
        severity=severity_map.get(new_rule.risk_level.value, "medium"),
        is_custom=True
    )

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    """Удаляет правило из custom_rules.yaml по ID"""
    if rule_id.startswith("sys-"):
        raise HTTPException(status_code=400, detail="Нельзя удалять системные правила")
    
    # Вызываем правильную функцию удаления по ID
    deleted = rules_manager.delete_custom_rule(rule_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Кастомное правило не найдено")
    
    return {"status": "deleted", "id": rule_id}