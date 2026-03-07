#!/usr/bin/env python
# tests/test_zip.py

import os
import sys
import json
import argparse
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scanner_engine import SecretScanner
from services.rules_manager import RulesManager
from services.file_handler import FileHandler
from core.severity import determine_severity

class ZipTester:
    """Тестирование сканирования ZIP проектов"""
    
    def __init__(self, use_entropy: bool = True):
        self.rules_manager = RulesManager()
        self.rules = self.rules_manager.get_enabled_rules()
        self.scanner = SecretScanner(self.rules, use_entropy=use_entropy)
        self.file_handler = FileHandler()
        
    def scan_zip(self, zip_path: str) -> dict:
        """
        Сканирует ZIP проект и возвращает JSON с результатами
        
        Args:
            zip_path: путь к ZIP файлу
            
        Returns:
            dict: результаты сканирования в формате JSON
        """
        start_time = datetime.now()
        
        # Проверяем существует ли файл
        if not os.path.exists(zip_path):
            return {
                "error": f"File not found: {zip_path}",
                "zip_file": str(zip_path),
                "status": "failed"
            }
        
        # Читаем ZIP
        try:
            with open(zip_path, 'rb') as f:
                zip_content = f.read()
        except Exception as e:
            return {
                "error": f"Cannot read ZIP file: {str(e)}",
                "zip_file": str(zip_path),
                "status": "failed"
            }
        
        # Создаем временный ID из имени файла
        scan_id = Path(zip_path).stem.replace(' ', '_')
        
        try:
            # Распаковываем
            extracted_dir = self.file_handler.extract_zip(zip_content, scan_id)
            
            # Сканируем
            extensions = self.file_handler.get_supported_extensions()
            findings_raw = self.scanner.scan_directory(extracted_dir, extensions=extensions)
            
            # Формируем результат
            result = self._format_results(zip_path, findings_raw, start_time)
            
            # Очистка
            self.file_handler.cleanup(scan_id)
            
            return result
            
        except zipfile.BadZipFile:
            return {
                "error": "Invalid ZIP file",
                "zip_file": str(zip_path),
                "status": "failed"
            }
        except Exception as e:
            # Пробуем очистить в случае ошибки
            try:
                self.file_handler.cleanup(scan_id)
            except:
                pass
                
            return {
                "error": str(e),
                "zip_file": str(zip_path),
                "status": "failed"
            }
    
    def scan_zip_batch(self, zip_paths: list) -> list:
        """Сканирует несколько ZIP файлов"""
        results = []
        total = len(zip_paths)
        
        for i, zip_path in enumerate(zip_paths, 1):
            print(f"📦 [{i}/{total}] Сканирую: {Path(zip_path).name}", file=sys.stderr)
            result = self.scan_zip(zip_path)
            results.append(result)
            
            if "error" in result:
                print(f"   ❌ Ошибка: {result['error']}", file=sys.stderr)
            else:
                print(f"   ✅ Найдено: {result['summary']['total_findings']} секретов", file=sys.stderr)
        
        return results
    
    def _format_results(self, zip_path: str, findings: list, start_time: datetime) -> dict:
        """Форматирует результаты в JSON"""
        duration = (datetime.now() - start_time).total_seconds()
        
        # Уникальные файлы с находками
        files_with_findings = set()
        for f in findings:
            files_with_findings.add(f.get('file_path', 'unknown'))
        
        # Статистика по уровням риска
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_rule = {}
        
        findings_list = []
        for f in findings:
            severity = determine_severity(f.get('risk_level', 'medium'), f.get('entropy'))
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            rule_name = f.get('rule_name', 'Unknown')
            by_rule[rule_name] = by_rule.get(rule_name, 0) + 1
            
            # Сокращаем путь до файла для читаемости
            file_path = f.get('file_path', 'unknown')
            if '\\' in file_path:
                # Пытаемся показать путь относительно проекта
                parts = file_path.split('\\')
                if len(parts) > 3:
                    file_path = '...\\' + '\\'.join(parts[-3:])
            
            findings_list.append({
                "file": file_path,
                "line": f.get('line_number'),
                "rule": rule_name,
                "severity": severity,
                "secret": f.get('secret_masked'),
                "entropy": round(f.get('entropy'), 2) if f.get('entropy') else None,
                "encoding": f.get('encoding_type')
            })
        
        return {
            "zip_file": str(zip_path),
            "scan_time": start_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "status": "success",
            "summary": {
                "total_files_scanned": len(files_with_findings),
                "total_findings": len(findings),
                "by_severity": by_severity,
                "by_rule": by_rule
            },
            "findings": findings_list
        }

def main():
    parser = argparse.ArgumentParser(
        description="Тестирование сканирования ZIP проектов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python test_zip.py project.zip
  python test_zip.py project1.zip project2.zip --pretty
  python test_zip.py *.zip --output results.json
  python test_zip.py folder/*.zip --no-entropy
        """
    )
    parser.add_argument("zips", nargs="+", help="ZIP файлы для сканирования")
    parser.add_argument("--output", "-o", help="Сохранить результат в файл")
    parser.add_argument("--pretty", action="store_true", help="Красивый вывод JSON с отступами")
    parser.add_argument("--no-entropy", action="store_true", help="Отключить анализ энтропии")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод в stderr")
    
    args = parser.parse_args()
    
    # Проверяем что файлы существуют
    valid_zips = []
    for zip_path in args.zips:
        # Поддержка wildcard (*.zip)
        if '*' in zip_path or '?' in zip_path:
            import glob
            expanded = glob.glob(zip_path)
            valid_zips.extend(expanded)
            if args.verbose:
                print(f"🔍 Найдено по шаблону {zip_path}: {len(expanded)} файлов", file=sys.stderr)
        elif os.path.exists(zip_path):
            if zip_path.endswith('.zip'):
                valid_zips.append(zip_path)
            else:
                print(f"⚠️ Не ZIP файл (пропущен): {zip_path}", file=sys.stderr)
        else:
            print(f"⚠️ Файл не найден (пропущен): {zip_path}", file=sys.stderr)
    
    if not valid_zips:
        print("❌ Нет валидных ZIP файлов для сканирования", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"📊 Всего файлов для сканирования: {len(valid_zips)}", file=sys.stderr)
        print(f"⚙️ Энтропийный анализ: {'ВКЛ' if not args.no_entropy else 'ВЫКЛ'}", file=sys.stderr)
    
    # Сканируем
    tester = ZipTester(use_entropy=not args.no_entropy)
    results = tester.scan_zip_batch(valid_zips)
    
    # Выводим JSON
    indent = 2 if args.pretty else None
    json_output = json.dumps(results, indent=indent, ensure_ascii=False, default=str)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"💾 Результаты сохранены в {args.output}", file=sys.stderr)
        
        # Если нужен краткий вывод в консоль
        if not args.pretty:
            total_findings = sum(r.get('summary', {}).get('total_findings', 0) for r in results if 'summary' in r)
            print(f"📊 Всего найдено секретов: {total_findings}", file=sys.stderr)
    else:
        print(json_output)

if __name__ == "__main__":
    main()