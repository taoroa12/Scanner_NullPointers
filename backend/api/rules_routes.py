from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter(prefix="/api/rules", tags=["Rules (Mock)"])

# Модель того, как выглядит правило
class Rule(BaseModel):
    id: str
    name: str
    pattern: str          # Само регулярное выражение
    severity: str         # critical, high, medium, low
    is_custom: bool       # True - создал юзер (можно удалить), False - системное (удалять нельзя)

# Временная "База данных" правил
MOCK_RULES = [
    Rule(id="sys-1", name="AWS Access Key", pattern="AKIA[0-9A-Z]{16}", severity="critical", is_custom=False),
    Rule(id="sys-2", name="Slack Token", pattern="xoxb-[0-9a-zA-Z\-]+", severity="high", is_custom=False),
    Rule(id="cust-1", name="Мой тестовый пароль", pattern="mypassword123", severity="medium", is_custom=True),
]

# Модель для создания нового правила (без ID и is_custom, их задает сервер)
class RuleCreate(BaseModel):
    name: str
    pattern: str
    severity: str

@router.get("/", response_model=List[Rule])
async def get_all_rules():
    """Отдает список всех правил (для отрисовки таблицы на фронте)"""
    return MOCK_RULES

@router.post("/", response_model=Rule)
async def add_custom_rule(rule_data: RuleCreate):
    """Добавляет новое пользовательское правило"""
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
    """Удаляет правило (только если оно кастомное)"""
    global MOCK_RULES
    
    # Ищем правило
    rule_to_delete = next((r for r in MOCK_RULES if r.id == rule_id), None)
    
    if not rule_to_delete:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    if not rule_to_delete.is_custom:
        raise HTTPException(status_code=400, detail="Cannot delete system rules")
        
    # Оставляем в списке все правила, кроме удаленного
    MOCK_RULES = [r for r in MOCK_RULES if r.id != rule_id]
    
    return {"status": "deleted", "id": rule_id}