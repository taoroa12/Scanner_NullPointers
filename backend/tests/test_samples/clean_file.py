# tests/test_samples/clean_file.py
# Этот файл НЕ содержит секретов - тест не должен ничего найти

import os
import sys
from datetime import datetime

def calculate_sum(a: int, b: int) -> int:
    """Обычная функция без секретов"""
    return a + b

def read_config():
    """Чтение конфига без паролей"""
    config_path = os.path.join("config", "settings.json")
    if os.path.exists(config_path):
        return {"debug": True, "port": 8000}
    return {}

class User:
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
    
    def greet(self):
        return f"Hello, {self.name}!"

# Обычные строки, не секреты
LOG_LEVEL = "INFO"
API_URL = "https://api.example.com/v1"
TIMEOUT = 30

if __name__ == "__main__":
    print(calculate_sum(5, 3))
    user = User("Test")
    print(user.greet())