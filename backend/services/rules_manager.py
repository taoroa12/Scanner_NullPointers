# services/rules_manager.py

import yaml
import re
from pathlib import Path
from typing import List, Optional, Dict
from models.schemas import Rule, RiskLevel, SecretType

class RulesManager:
    """Менеджер для загрузки и управления правилами"""
    
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "rules" / "default_rules.yaml"
        self.rules_path = rules_path
        self.rules = []
        self.load_rules()
    
    def load_rules(self) -> List[Rule]:
        """Загружает правила из YAML файла"""
        if not Path(self.rules_path).exists():
            print(f"⚠️ Файл {self.rules_path} не найден")
            return []
        
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            self.rules = []
            for rule_data in rules_data:
                try:
                    # Преобразуем secret_type в нижний регистр
                    secret_type_raw = rule_data.get('secret_type', 'GENERIC')
                    secret_type_str = secret_type_raw.lower()
                    
                    rule = Rule(
                        name=rule_data['name'],
                        pattern=rule_data['pattern'],
                        risk_level=RiskLevel(rule_data['risk_level'].lower()),
                        secret_type=SecretType(secret_type_str),
                        description=rule_data.get('description', ''),
                        enabled=True,
                        entropy_threshold=rule_data.get('entropy_threshold')
                    )
                    self.rules.append(rule)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки правила {rule_data.get('name', 'unknown')}: {e}")
            
            print(f"✅ Загружено правил: {len(self.rules)}")
            return self.rules
            
        except Exception as e:
            print(f"❌ Ошибка загрузки YAML: {e}")
            return []
    
    def get_enabled_rules(self) -> List[Rule]:
        """Возвращает только активные правила"""
        return [r for r in self.rules if r.enabled]
    
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
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            for rule_data in rules_data:
                if 'recommendation' in rule_data:
                    recommendations[rule_data['name']] = rule_data['recommendation']
        except:
            pass
        return recommendations