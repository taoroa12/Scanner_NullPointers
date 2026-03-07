# services/rules_manager.py
import yaml
import re
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from models.schemas import Rule, RiskLevel, SecretType

class RulesManager:
    """Менеджер для загрузки и управления правилами"""
    
    def __init__(self, rules_path: str = None, custom_rules_path: str = None):
        base_dir = Path(__file__).parent.parent
        if rules_path is None:
            rules_path = base_dir / "rules" / "default_rules.yaml"
        if custom_rules_path is None:
            custom_rules_path = base_dir / "rules" / "custom_rules.yaml"
            
        self.rules_path = Path(rules_path)
        self.custom_rules_path = Path(custom_rules_path)
        self.rules = []
        self.custom_rules = []
        self.load_rules()
        self.load_custom_rules()
    
    def load_rules(self) -> List[Rule]:
        """Загружает правила из YAML файла"""
        if not self.rules_path.exists():
            print(f"⚠️ Файл {self.rules_path} не найден")
            return []
        
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            self.rules = []
            for i, rule_data in enumerate(rules_data, start=1):
                try:
                    # Преобразуем secret_type в нижний регистр
                    secret_type_raw = rule_data.get('secret_type', 'GENERIC')
                    secret_type_str = secret_type_raw.lower()
                    
                    rule = Rule(
                        id=f"sys-{i}",
                        name=rule_data['name'],
                        pattern=rule_data['pattern'],
                        risk_level=RiskLevel(rule_data['risk_level'].lower()),
                        secret_type=SecretType(secret_type_str),
                        description=rule_data.get('description', ''),
                        recommendation=rule_data.get('recommendation', ''),
                        enabled=True,
                        entropy_threshold=rule_data.get('entropy_threshold'),
                        is_custom=False
                    )
                    self.rules.append(rule)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки правила {rule_data.get('name', 'unknown')}: {e}")
            
            print(f"✅ Загружено системных правил: {len(self.rules)}")
            return self.rules
            
        except Exception as e:
            print(f"❌ Ошибка загрузки YAML: {e}")
            return []
    
    def load_custom_rules(self) -> List[Rule]:
        """Загружает пользовательские правила из YAML"""
        if not self.custom_rules_path.exists():
            return []
        
        try:
            with open(self.custom_rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f) or []
            
            self.custom_rules = []
            for rule_data in rules_data:
                try:
                    rule = Rule(
                        id=rule_data.get('id'),
                        name=rule_data['name'],
                        pattern=rule_data['pattern'],
                        risk_level=RiskLevel(rule_data['risk_level'].lower()),
                        secret_type=SecretType(rule_data.get('secret_type', 'generic').lower()),
                        description=rule_data.get('description', ''),
                        enabled=rule_data.get('enabled', True),
                        is_custom=True
                    )
                    self.custom_rules.append(rule)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки кастомного правила: {e}")
            
            print(f"✅ Загружено пользовательских правил: {len(self.custom_rules)}")
            return self.custom_rules
        except Exception as e:
            print(f"❌ Ошибка загрузки YAML кастомных правил: {e}")
            return []

    def save_custom_rules(self):
        """Сохраняет пользовательские правила в YAML"""
        try:
            self.custom_rules_path.parent.mkdir(parents=True, exist_ok=True)
            # Конвертируем в dict для сохранения в YAML
            data = []
            for r in self.custom_rules:
                data.append({
                    "id": r.id,
                    "name": r.name,
                    "pattern": r.pattern,
                    "risk_level": r.risk_level.value,
                    "secret_type": r.secret_type.value,
                    "description": r.description,
                    "enabled": r.enabled
                })
                
            with open(self.custom_rules_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"❌ Ошибка сохранения кастомных правил: {e}")

    def add_custom_rule(self, name: str, pattern: str, severity: str) -> Rule:
        """Добавляет новое пользовательское правило"""
        # Map severity (frontend) to RiskLevel (backend)
        risk_map = {
            "critical": RiskLevel.HIGH,
            "high": RiskLevel.HIGH,
            "medium": RiskLevel.MEDIUM,
            "low": RiskLevel.LOW
        }
        
        new_rule = Rule(
            id=f"cust-{str(uuid.uuid4())[:6]}",
            name=name,
            pattern=pattern,
            risk_level=risk_map.get(severity, RiskLevel.MEDIUM),
            is_custom=True
        )
        self.custom_rules.append(new_rule)
        self.save_custom_rules()
        return new_rule

    def delete_custom_rule(self, rule_id: str) -> bool:
        """Удаляет пользовательское правило по ID"""
        initial_len = len(self.custom_rules)
        self.custom_rules = [r for r in self.custom_rules if r.id != rule_id]
        if len(self.custom_rules) < initial_len:
            self.save_custom_rules()
            return True
        return False

    def get_enabled_rules(self) -> List[Rule]:
        """Возвращает только активные правила (системные + кастомные)"""
        # Перезагружаем кастомные правила перед получением, чтобы учесть изменения из других роутов
        self.load_custom_rules()
        
        system_enabled = [r for r in self.rules if r.enabled]
        custom_enabled = [r for r in self.custom_rules if r.enabled]
        return system_enabled + custom_enabled
    
    def validate_pattern(self, pattern: str) -> bool:
        """Проверяет корректность regex паттерна"""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
    
    def get_recommendations(self) -> Dict[str, str]:
        """Загружает рекомендации из правил"""
        recommendations = {}
        try:
            # Сначала системные
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            for rule_data in rules_data:
                if 'recommendation' in rule_data:
                    recommendations[rule_data['name']] = rule_data['recommendation']
            
            # Потом кастомные (если есть рекомендации)
            for r in self.custom_rules:
                if r.description:
                    recommendations[r.name] = r.description
        except:
            pass
        return recommendations
