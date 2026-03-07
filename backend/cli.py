# backend/cli.py

import argparse
import sys
import os
import json
from pathlib import Path

# Добавляем путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

from core.scanner_engine import SecretScanner
from services.rules_manager import RulesManager
from services.file_handler import FileHandler
from core.severity import determine_severity

# ANSI цвета для красивого вывода в консоль
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("==================================================")
    print("🔍 SECRET SCANNER CLI - Поиск утечек в коде")
    print("==================================================")
    print(f"{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Локальный сканер секретов в коде.")
    parser.add_argument("path", help="Путь к папке или файлу для сканирования (например: . или ./my_project)")
    parser.add_argument("--format", choices=['text', 'json'], default='text', help="Формат вывода (text или json)")
    parser.add_argument("--no-color", action="store_true", help="Отключить цветной вывод (для логов)")
    
    args = parser.parse_args()
    # Если просят выключить цвета - зануляем все ANSI коды в классе Colors
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')
    scan_path = Path(args.path)

    if not scan_path.exists():
        print(f"{Colors.FAIL}❌ Ошибка: Путь '{scan_path}' не существует!{Colors.ENDC}")
        sys.exit(1)

    if args.format == 'text':
        print_banner()
        print(f"⏳ Инициализация сканера... Загрузка правил.")

    # Инициализируем компоненты
    rules_manager = RulesManager()
    rules = rules_manager.get_enabled_rules()
    
    if not rules:
        print(f"{Colors.FAIL}❌ Ошибка: Нет активных правил для сканирования!{Colors.ENDC}")
        sys.exit(1)

    scanner = SecretScanner(rules, use_entropy=True)
    file_handler = FileHandler()
    
    if args.format == 'text':
        print(f"🚀 Запуск сканирования директории: {Colors.BOLD}{scan_path.absolute()}{Colors.ENDC}\n")

    # Запускаем сканирование
    extensions = file_handler.get_supported_extensions()
    findings_raw = scanner.scan_directory(str(scan_path), extensions=extensions)

    # Если выбрали JSON формат
    if args.format == 'json':
        print(json.dumps(findings_raw, indent=2, ensure_ascii=False))
        sys.exit(0)

    # Если выбрали текстовый формат
    if not findings_raw:
        print(f"{Colors.OKGREEN}✅ Поздравляем! Секретов не найдено. Код чист.{Colors.ENDC}")
        sys.exit(0)

       # Статистика (считаем все 4 уровня)
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}🚨 РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ:{Colors.ENDC}")
    
    for i, f in enumerate(findings_raw, 1):
        rule_name = f.get('rule_name', 'Unknown')
        file_p = f.get('file_path', 'unknown')
        line = f.get('line_number', 0)
        secret = f.get('secret_masked', '***')
        entropy = f.get('entropy')

        # ✅ Используем финальную критичность (с учетом энтропии)
        severity = determine_severity(f.get('risk_level', 'low'), entropy).upper()

        # Выбираем цвет и считаем статистику
        if severity == 'CRITICAL':
            critical_count += 1
            color = Colors.FAIL
        elif severity == 'HIGH':
            high_count += 1
            color = Colors.WARNING
        elif severity == 'MEDIUM':
            medium_count += 1
            color = Colors.OKCYAN
        else:
            low_count += 1
            color = Colors.OKBLUE

        ent_text = f" (Энтропия: {entropy:.2f})" if entropy else ""
        
        print(f"{color}[{severity}] {rule_name}{Colors.ENDC}")
        print(f"  📍 Файл:   {file_p}:{line}")
        print(f"  🔑 Секрет: {secret}{ent_text}")
        print("-" * 50)

    print(f"\n{Colors.BOLD}📊 ИТОГО:{Colors.ENDC}")
    print(f"Всего находок: {len(findings_raw)}")
    print(f"🔴 CRITICAL: {Colors.FAIL}{critical_count}{Colors.ENDC}")
    print(f"🟠 HIGH:     {Colors.WARNING}{high_count}{Colors.ENDC}")
    print(f"🟡 MEDIUM:   {Colors.OKCYAN}{medium_count}{Colors.ENDC}")
    print(f"🟢 LOW:      {Colors.OKBLUE}{low_count}{Colors.ENDC}")
if __name__ == "__main__":
    if os.name == 'nt':
        os.system('color')
    
    main()