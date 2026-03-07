# core/scanner_engine.py

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from models.schemas import Rule, Finding, SecretType, RiskLevel
from core.severity import mask_secret, determine_severity  # исправлен импорт
from core.entropy import analyze_secret_entropy

class SecretScanner:
    """
    Основной движок для сканирования секретов в файлах
    """
    
    def __init__(self, rules: List[Rule], use_entropy: bool = True):
        """
        Инициализация сканера с правилами поиска
        
        Args:
            rules: список объектов Rule с паттернами поиска
            use_entropy: использовать ли анализ энтропии
        """
        self.rules = rules
        self.use_entropy = use_entropy
        self.compiled_rules = []
        
        # Компилируем все regex заранее для производительности
        for rule in rules:
            if rule.enabled:
                try:
                    compiled = re.compile(rule.pattern, re.IGNORECASE)
                    rule_info = {
                        "name": rule.name,
                        "pattern": rule.pattern,
                        "compiled": compiled,
                        "risk_level": rule.risk_level,
                        "secret_type": rule.secret_type,
                        "description": rule.description,
                        "entropy_threshold": getattr(rule, 'entropy_threshold', None)
                    }
                    self.compiled_rules.append(rule_info)
                except re.error as e:
                    print(f"⚠️ Ошибка в regex правила '{rule.name}': {e}")
    
    def scan_line(self, line: str, line_number: int, file_path: str) -> List[Dict[str, Any]]:
        """
        Сканирует одну строку на наличие секретов по всем правилам
        ВОЗВРАЩАЕТ СЛОВАРЬ, а не Finding (чтобы избежать ошибок валидации)
        
        Args:
            line: текст строки
            line_number: номер строки в файле
            file_path: путь к файлу
            
        Returns:
            List[Dict]: список найденных секретов в этой строке (как словари)
        """
        findings = []
        
        # Пропускаем пустые строки
        if not line or not line.strip():
            return findings
        
        # Проходим по всем скомпилированным правилам
        for rule_info in self.compiled_rules:
            try:
                # Ищем все совпадения в строке
                matches = rule_info["compiled"].finditer(line)
                
                for match in matches:
                    # Получаем найденный секрет
                    secret_value = match.group()
                    
                    # Пропускаем слишком короткие строки
                    if len(secret_value) < 4:
                        continue
                    
                    # Анализ энтропии (если включен)
                    entropy_value = None
                    encoding_type = None
                    risk_level = rule_info["risk_level"]
                    
                    if self.use_entropy and len(secret_value) >= 8:
                        entropy_analysis = analyze_secret_entropy(secret_value)
                        entropy_value = entropy_analysis['entropy']
                        encoding_type = entropy_analysis['encoding']
                        
                        # Проверяем пороги энтропии для правила
                        threshold = rule_info.get("entropy_threshold")
                        if threshold and entropy_value < threshold:
                            continue  # Пропускаем если энтропия ниже порога
                        
                        # Повышаем риск если энтропия высокая
                        if entropy_analysis['is_high_risk']:
                            if risk_level == RiskLevel.LOW:
                                risk_level = RiskLevel.MEDIUM
                            elif risk_level == RiskLevel.MEDIUM:
                                risk_level = RiskLevel.HIGH
                    
                    # Маскируем секрет
                    masked_value = mask_secret(secret_value)
                    
                    # ВОЗВРАЩАЕМ СЛОВАРЬ, а не Finding
                    finding_dict = {
                        "file_path": file_path,
                        "line_number": line_number,
                        "rule_name": rule_info["name"],
                        "secret_type": rule_info["secret_type"].value,
                        "risk_level": risk_level.value,
                        "secret_masked": masked_value,
                        "line_content": line.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "entropy": entropy_value,
                        "encoding_type": encoding_type
                    }
                    
                    findings.append(finding_dict)
                    
            except Exception as e:
                print(f"   ⚠️ Ошибка при применении правила {rule_info['name']}: {e}")
                continue
        
        return findings
    
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Сканирует весь файл на наличие секретов
        
        Args:
            file_path: путь к файлу для сканирования
            
        Returns:
            List[Dict]: список всех находок в файле (как словари)
        """
        all_findings = []
        file_path_obj = Path(file_path)
        
        # Проверяем существует ли файл
        if not file_path_obj.exists():
            print(f"   ⚠️ Файл не существует: {file_path}")
            return []
        
        # Проверяем размер файла (пропускаем файлы больше 10 MB)
        try:
            file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            if file_size_mb > 10:
                print(f"   ⚠️ Файл слишком большой ({file_size_mb:.1f} MB), пропускаем: {file_path}")
                return []
        except:
            pass  # Если не можем получить размер, продолжаем
        
        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1', 'utf-16', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        # Сканируем каждую строку
                        line_findings = self.scan_line(
                            line=line,
                            line_number=line_num,
                            file_path=str(file_path)
                        )
                        all_findings.extend(line_findings)
                break  # если успешно прочитали, выходим из цикла кодировок
                
            except UnicodeDecodeError:
                continue  # пробуем следующую кодировку
            except PermissionError:
                print(f"   ⚠️ Нет прав на чтение: {file_path}")
                return []
            except Exception as e:
                print(f"   ⚠️ Ошибка чтения {file_path}: {e}")
                return []
        
        return all_findings
    
    def scan_directory(self, directory_path: str, extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Сканирует все файлы в директории
        
        Args:
            directory_path: путь к директории
            extensions: список расширений для сканирования
            
        Returns:
            List[Dict]: все находки в директории (всегда возвращает список словарей)
        """
        all_findings = []
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            print(f"❌ Директория не существует: {directory_path}")
            return []  # Всегда возвращаем список, даже пустой
        
        # Папки которые всегда пропускаем
        exclude_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', 'env', 
            '.venv', 'dist', 'build', '.idea', '.vscode', 
            'site-packages', 'vendor', 'bower_components'
        }
        
        print(f"\n🔍 Сканируем директорию: {directory_path}")
        
        files_scanned = 0
        files_with_findings = 0
        
        try:
            # Рекурсивно обходим все файлы
            for root, dirs, files in os.walk(directory):
                # Исключаем ненужные папки
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                # Также исключаем скрытые папки (начинающиеся с точки)
                dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Проверяем расширение файла
                    if extensions:
                        if file_path.suffix.lower() not in extensions:
                            continue
                    
                    # Пропускаем бинарные расширения
                    binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', 
                                        '.ico', '.pdf', '.zip', '.tar', '.gz', 
                                        '.exe', '.dll', '.so', '.dylib', '.class'}
                    if file_path.suffix.lower() in binary_extensions:
                        continue
                    
                    # Сканируем файл
                    try:
                        findings = self.scan_file(str(file_path))
                        if findings:  # если есть находки
                            all_findings.extend(findings)
                            files_with_findings += 1
                            
                            # Показываем прогресс для файлов с находками
                            rel_path = file_path.relative_to(directory)
                            print(f"   🔍 Найдено в {rel_path}: {len(findings)} секретов")
                            
                    except Exception as e:
                        print(f"   ⚠️ Ошибка сканирования {file_path}: {e}")
                    
                    files_scanned += 1
                    
                    # Прогресс (каждые 100 файлов)
                    if files_scanned % 100 == 0:
                        print(f"   ⏳ Просканировано файлов: {files_scanned}, найдено секретов: {len(all_findings)}")
        
        except KeyboardInterrupt:
            print(f"\n   ⚠️ Сканирование прервано пользователем")
            return all_findings  # Возвращаем то, что уже нашли
            
        except Exception as e:
            print(f"❌ Ошибка при обходе директории: {e}")
        
        print(f"\n✅ Сканирование завершено!")
        print(f"   📊 Файлов просканировано: {files_scanned}")
        print(f"   📁 Файлов с находками: {files_with_findings}")
        print(f"   🔑 Всего находок: {len(all_findings)}")
        
        return all_findings  # Всегда возвращаем список
    
    def get_statistics(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Возвращает статистику по находкам
        
        Args:
            findings: список находок (словарей)
            
        Returns:
            Dict со статистикой
        """
        stats = {
            'total': len(findings),
            'by_risk': {
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'by_type': {},
            'by_file': {},
            'high_entropy': 0
        }
        
        for finding in findings:
            # По уровням риска
            risk = finding.get('risk_level', 'low')
            stats['by_risk'][risk] = stats['by_risk'].get(risk, 0) + 1
            
            # По типам секретов
            secret_type = finding.get('secret_type', 'unknown')
            stats['by_type'][secret_type] = stats['by_type'].get(secret_type, 0) + 1
            
            # По файлам
            file_path = finding.get('file_path', 'unknown')
            stats['by_file'][file_path] = stats['by_file'].get(file_path, 0) + 1
            
            # Высокая энтропия
            entropy = finding.get('entropy')
            if entropy and entropy > 4.5:
                stats['high_entropy'] += 1
        
        return stats

# === Пример использования ===
if __name__ == "__main__":
    # Создаем несколько тестовых правил
    from models.schemas import Rule, RiskLevel, SecretType
    
    test_rules = [
        Rule(
            name="AWS Key",
            pattern=r"AKIA[0-9A-Z]{16}",
            risk_level=RiskLevel.HIGH,
            secret_type=SecretType.AWS_KEY,
            description="AWS Access Key ID"
        ),
        Rule(
            name="GitHub Token",
            pattern=r"ghp_[a-zA-Z0-9]{36}",
            risk_level=RiskLevel.HIGH,
            secret_type=SecretType.TOKEN,
            description="GitHub Personal Access Token"
        ),
    ]
    
    # Создаем сканер
    scanner = SecretScanner(test_rules, use_entropy=True)
    
    # Тест сканирования строки
    test_line = "aws_key = 'AKIAIOSFODNN7EXAMPLE'"
    findings = scanner.scan_line(test_line, 1, "test.py")
    
    print(f"Найдено секретов: {len(findings)}")
    for f in findings:
        print(f"  - {f['rule_name']}: {f['secret_masked']} (риск: {f['risk_level']})")