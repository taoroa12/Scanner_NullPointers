from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import uuid
import re  # Библиотека для работы с регулярными выражениями

router = APIRouter(prefix="/api/rules", tags=["Rules (Mock)"])

class Rule(BaseModel):
    id: str
    name: str
    pattern: str
    severity: str
    is_custom: bool

MOCK_RULES = [
    Rule(id="sys-1", name="AWS Access Key", pattern="AKIA[0-9A-Z]{16}", severity="critical", is_custom=False),
    Rule(id="sys-2", name="Slack Token", pattern="xoxb-[0-9a-zA-Z\-]+", severity="high", is_custom=False),
]

# ОБНОВЛЕННАЯ МОДЕЛЬ (С жесткими правилами от Pydantic)
class RuleCreate(BaseModel):
    # min_length=1 запрещает присылать пустые строки ""
    name: str = Field(..., min_length=1, description="Название правила")
    pattern: str = Field(..., min_length=1, description="Регулярное выражение (Regex)")
    
    # Literal заставит Pydantic автоматически отбивать всё, кроме этих 4 слов
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Уровень угрозы")

@router.get("/", response_model=List[Rule])
async def get_all_rules():
    return MOCK_RULES

@router.post("/", response_model=Rule)
async def add_custom_rule(rule_data: RuleCreate):
    
    # ==========================================
    # ПРОВЕРКА №1: Валидация регулярного выражения
    # ==========================================
    try:
        re.compile(rule_data.pattern)
    except re.error:
        # Если регулярка кривая, кидаем понятную ошибку фронтенду
        raise HTTPException(
            status_code=400, 
            detail="Ошибка синтаксиса в регулярном выражении (Invalid Regex)"
        )

    # Если всё ок, создаем правило
    new_rule = Rule(
        id=f"cust-{str(uuid.uuid4())[:6]}",
        name=rule_data.name,
        pattern=rule_data.pattern,
        severity=rule_data.severity,
        is_custom=True
    )
    MOCK_RULES.append(new_rule)
    return new_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    global MOCK_RULES
    
    rule_to_delete = next((r for r in MOCK_RULES if r.id == rule_id), None)
    
    if not rule_to_delete:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    if not rule_to_delete.is_custom:
        raise HTTPException(status_code=400, detail="Cannot delete system rules")
        
    MOCK_RULES = [r for r in MOCK_RULES if r.id != rule_id]
    
    return {"status": "deleted", "id": rule_id}