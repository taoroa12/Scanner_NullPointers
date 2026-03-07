from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import uuid
import re

from services.rules_manager import RulesManager  # ← ДОБАВЬ ЭТОТ ИМПОРТ

router = APIRouter(prefix="/api/rules", tags=["Rules (Mock)"])

# Создаем экземпляр RulesManager для работы с YAML правилами
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
    """Возвращает все правила из YAML + системные"""
    
    # Загружаем правила из YAML через RulesManager
    yaml_rules = rules_manager.get_enabled_rules()
    
    # Конвертируем в формат ответа
    rules_response = []
    
    # Добавляем системные правила (из MOCK_RULES)
    rules_response.append({
        "id": "sys-1",
        "name": "AWS Access Key",
        "pattern": "AKIA[0-9A-Z]{16}",
        "severity": "critical",
        "is_custom": False
    })
    
    rules_response.append({
        "id": "sys-2",
        "name": "Slack Token",
        "pattern": "xoxb-[0-9a-zA-Z\\-]+",
        "severity": "high",
        "is_custom": False
    })
    
    # Добавляем правила из YAML
    for i, rule in enumerate(yaml_rules, start=3):
        # Конвертируем risk_level в severity
        severity_map = {
            "high": "critical" if rule.name == "AWS Access Key" else "high",
            "medium": "medium",
            "low": "low"
        }
        
        rules_response.append({
            "id": f"rule-{i}",
            "name": rule.name,
            "pattern": rule.pattern,
            "severity": severity_map.get(rule.risk_level.value, "medium"),
            "is_custom": False
        })
    
    return rules_response

@router.post("/", response_model=RuleResponse)
async def add_custom_rule(rule_data: RuleCreate):
    """Добавляет пользовательское правило"""
    
    # Проверка регулярного выражения
    try:
        re.compile(rule_data.pattern)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid Regex")
    
    # Здесь можно добавить сохранение в БД или файл
    # Пока просто возвращаем созданное правило
    
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
    
    # Здесь должна быть логика удаления из БД/файла
    
    return {"status": "deleted", "id": rule_id}