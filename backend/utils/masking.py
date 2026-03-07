# utils/masking.py

def mask_secret(value: str, visible_start: int = 4, visible_end: int = 4, mask_char: str = "*") -> str:
    """
    Маскирует секрет, показывая только первые и последние символы
    
    Args:
        value: исходный секрет
        visible_start: сколько символов показать в начале
        visible_end: сколько символов показать в конце
        mask_char: символ для маскировки
    
    Returns:
        замаскированная строка
    """
    if not value:
        return ""
    
    length = len(value)
    
    # Для очень коротких секретов
    if length <= visible_start + visible_end:
        return mask_char * 3
    
    # Для длинных секретов
    start = value[:visible_start]
    end = value[-visible_end:]
    masked = mask_char * 3
    
    return f"{start}{masked}{end}"

# Тест
if __name__ == "__main__":
    print(mask_secret("sk-1234567890", 3, 3))  # sk-***890
    print(mask_secret("AKIAIOSFODNN7EXAMPLE"))  # AKIA***MPLE
    print(mask_secret("short"))  # ***