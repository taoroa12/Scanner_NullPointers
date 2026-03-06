# core/entropy.py

import math
import re
from collections import Counter
from typing import Union, Optional

def shannon_entropy(data: Union[str, bytes]) -> float:
    """
    Рассчитывает энтропию Шеннона для строки/данных
    
    Args:
        data: строка или байты для анализа
        
    Returns:
        float: значение энтропии (от 0 до 8 для байт, выше для строк)
    """
    if not data:
        return 0.0
    
    # Если строка - конвертируем в байты
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Считаем частоту каждого байта
    data_len = len(data)
    if data_len == 0:
        return 0.0
    
    freq = Counter(data)
    
    # Рассчитываем энтропию по формуле Шеннона
    entropy = 0.0
    for count in freq.values():
        prob = count / data_len
        entropy -= prob * math.log2(prob)
    
    return entropy

def is_high_entropy_string(text: str, threshold: float = 3.5) -> bool:
    """
    Проверяет, является ли строка высокоэнтропийной
    
    Args:
        text: строка для проверки
        threshold: порог энтропии (обычно 3.5-4.5)
        
    Returns:
        bool: True если энтропия выше порога
    """
    if not text or len(text) < 8:
        return False
    
    entropy = shannon_entropy(text)
    return entropy > threshold

def detect_encoding_type(text: str) -> Optional[str]:
    """
    Определяет тип кодировки строки (hex, base64, или обычный текст)
    
    Args:
        text: строка для анализа
        
    Returns:
        str: 'hex', 'base64', 'text' или None
    """
    if not text:
        return None
    
    # Проверка на hex (только символы 0-9, a-f, A-F)
    hex_pattern = re.match(r'^[0-9a-fA-F]+$', text)
    if hex_pattern and len(text) % 2 == 0:  # hex обычно четной длины
        return 'hex'
    
    # Проверка на base64 (символы a-z, A-Z, 0-9, +, /, =)
    base64_pattern = re.match(r'^[a-zA-Z0-9+/]+={0,2}$', text)
    if base64_pattern and len(text) >= 16:
        return 'base64'
    
    # Проверка на смешанный текст
    if any(c.isalpha() for c in text) and any(c.isdigit() for c in text):
        return 'mixed'
    
    return 'text'

def analyze_secret_entropy(secret: str) -> dict:
    """
    Полный анализ энтропии секрета
    
    Args:
        secret: строка с потенциальным секретом
        
    Returns:
        dict: результаты анализа
    """
    result = {
        'entropy': shannon_entropy(secret),
        'encoding': detect_encoding_type(secret),
        'length': len(secret),
        'is_high_risk': False,
        'risk_factors': []
    }
    
    # Определяем риск на основе энтропии и кодировки
    encoding = result['encoding']
    entropy = result['entropy']
    
    if encoding == 'hex' and entropy > 3.5:
        result['is_high_risk'] = True
        result['risk_factors'].append(f"Высокая энтропия для hex: {entropy:.2f} > 3.5")
    
    if encoding == 'base64' and entropy > 4.5:
        result['is_high_risk'] = True
        result['risk_factors'].append(f"Высокая энтропия для base64: {entropy:.2f} > 4.5")
    
    if encoding == 'mixed' and entropy > 4.0:
        result['is_high_risk'] = True
        result['risk_factors'].append(f"Высокая энтропия для смешанного текста: {entropy:.2f} > 4.0")
    
    # Очень длинные строки с высокой энтропией
    if len(secret) > 40 and entropy > 4.5:
        result['is_high_risk'] = True
        result['risk_factors'].append(f"Длинная строка ({len(secret)} символов) с высокой энтропией")
    
    return result

# Тесты
if __name__ == "__main__":
    test_strings = [
        ("AKIAIOSFODNN7EXAMPLE", "AWS Key"),
        ("ghp_123456789012345678901234567890123456", "GitHub Token"),
        ("hello world this is normal text", "Normal text"),
        ("1234567890", "Just numbers"),
        ("a1b2c3d4e5f6g7h8i9j0", "Mixed"),
        ("-----BEGIN RSA PRIVATE KEY-----", "Private key header"),
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "JWT part"),
    ]
    
    print("=== Анализ энтропии ===\n")
    for text, name in test_strings:
        analysis = analyze_secret_entropy(text)
        print(f"{name}:")
        print(f"  Текст: {text[:30]}..." if len(text) > 30 else f"  Текст: {text}")
        print(f"  Энтропия: {analysis['entropy']:.2f}")
        print(f"  Кодировка: {analysis['encoding']}")
        print(f"  Высокий риск: {analysis['is_high_risk']}")
        if analysis['risk_factors']:
            print(f"  Факторы риска: {', '.join(analysis['risk_factors'])}")
        print()