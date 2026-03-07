# tests/test_scanner.py

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scanner_engine import SecretScanner
from services.rules_manager import RulesManager
from core.severity import mask_secret

class TestSecretScanner(unittest.TestCase):
    """Тесты для сканера секретов"""
    
    @classmethod
    def setUpClass(cls):
        """Загружаем правила один раз для всех тестов"""
        cls.rules_manager = RulesManager()
        cls.rules = cls.rules_manager.get_enabled_rules()
        cls.scanner = SecretScanner(cls.rules, use_entropy=True)
        
        # Пути к тестовым файлам
        cls.test_samples_dir = Path(__file__).parent / "test_samples"
    
    def test_scan_file_with_secrets(self):
        """Позитивный тест: файл с секретами должен найти находки"""
        test_file = self.test_samples_dir / "secret_file.py"
        self.assertTrue(test_file.exists(), f"Тестовый файл не найден: {test_file}")
        
        findings = self.scanner.scan_file(str(test_file))
        
        # Должны найти минимум 5 секретов
        self.assertGreaterEqual(len(findings), 5, 
                               f"Найдено только {len(findings)} секретов, ожидалось минимум 5")
        
        # Проверяем конкретные секреты
        secret_values = [f['secret_masked'] for f in findings]
        
        # Проверяем AWS ключ
        aws_found = any("AKIA" in f['secret_masked'] for f in findings)
        self.assertTrue(aws_found, "AWS ключ не найден")
        
        # Проверяем GitHub токен
        github_found = any("ghp_" in f['secret_masked'] for f in findings)
        self.assertTrue(github_found, "GitHub токен не найден")
        
        # Проверяем Stripe ключ
        stripe_found = any("sk_live" in f['secret_masked'] for f in findings)
        self.assertTrue(stripe_found, "Stripe ключ не найден")
        
        print(f"\n✅ Найдено секретов: {len(findings)}")
        for f in findings:
            print(f"   - {f['rule_name']}: {f['secret_masked']} (строка {f['line_number']})")
    
    def test_scan_clean_file(self):
        """Негативный тест: чистый файл не должен найти секреты"""
        test_file = self.test_samples_dir / "clean_file.py"
        self.assertTrue(test_file.exists(), f"Тестовый файл не найден: {test_file}")
        
        findings = self.scanner.scan_file(str(test_file))
        
        # Не должно быть находок
        self.assertEqual(len(findings), 0, 
                        f"Найдены секреты в чистом файле: {len(findings)}")
        
        print("\n✅ Чистый файл просканирован, секретов не найдено")
    
    def test_scan_nonexistent_file(self):
        """Тест на несуществующий файл"""
        findings = self.scanner.scan_file("nonexistent_file_12345.py")
        self.assertEqual(len(findings), 0, "Несуществующий файл должен возвращать пустой список")
    
    def test_scan_empty_file(self):
        """Тест на пустой файл"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            findings = self.scanner.scan_file(temp_file)
            self.assertEqual(len(findings), 0, "Пустой файл не должен содержать секреты")
        finally:
            os.unlink(temp_file)
    
    def test_binary_file_skip(self):
        """Тест на бинарный файл - должен быть пропущен"""
        test_file = self.test_samples_dir / "binary_file.jpg"
        
        # Создаем бинарный файл если его нет
        if not test_file.exists():
            with open(test_file, 'wb') as f:
                f.write(b'\x00\x01\x02\x03\x04\x05')  # бинарные данные
        
        findings = self.scanner.scan_file(str(test_file))
        
        # Бинарный файл должен вернуть пустой список (пропущен)
        self.assertEqual(len(findings), 0, "Бинарный файл должен быть пропущен")
        print("\n✅ Бинарный файл пропущен")
    
    def test_large_file_skip(self):
        """Тест на большой файл (>10MB) - должен быть пропущен"""
        test_file = self.test_samples_dir / "large_file.py"
        
        # Создаем большой файл если его нет
        if not test_file.exists():
            with open(test_file, 'w') as f:
                # Пишем 11 MB данных
                for _ in range(1100):
                    f.write("x" * 1024 * 10 + "\n")
        
        findings = self.scanner.scan_file(str(test_file))
        
        # Большой файл должен вернуть пустой список (пропущен)
        self.assertEqual(len(findings), 0, "Файл >10MB должен быть пропущен")
        print("\n✅ Большой файл пропущен")
    
    def test_entropy_calculation(self):
        """Тест расчета энтропии"""
        test_file = self.test_samples_dir / "secret_file.py"
        
        findings = self.scanner.scan_file(str(test_file))
        
        # Проверяем что энтропия считается
        for f in findings:
            self.assertIn('entropy', f, "Энтропия должна быть в результатах")
            if f['entropy']:
                self.assertIsInstance(f['entropy'], float)
                print(f"   {f['rule_name']}: энтропия {f['entropy']:.2f}")
    
    def test_masking_function(self):
        """Тест функции маскирования"""
        test_cases = [
            ("AKIAIOSFODNN7EXAMPLE", "AKIA***MPLE"),
            ("ghp_123456789012345678901234567890123456", "ghp_***3456"),
            ("short", "***"),
            ("", ""),
        ]
        
        for input_val, expected in test_cases:
            result = mask_secret(input_val)
            self.assertEqual(result, expected, 
                           f"Маскирование '{input_val}' дало '{result}', ожидалось '{expected}'")
        
        print("\n✅ Функция маскирования работает")
    
    def test_directory_scan(self):
        """Тест сканирования всей директории"""
        findings = self.scanner.scan_directory(
            str(self.test_samples_dir),
            extensions=['.py']
        )
        
        # Должны найти секреты хотя бы в одном файле
        self.assertGreater(len(findings), 0, 
                          "Директория должна содержать секреты")
        
        print(f"\n✅ Директория просканирована, найдено {len(findings)} секретов")

if __name__ == "__main__":
    unittest.main(verbosity=2)