from typing import Optional
from models.schemas import RiskLevel

def mask_secret(value: str, visible_start: int = 4, visible_end: int = 4, mask_char: str = "*") -> str:
    """
    Маскирует секрет, показывая только первые и последние символы
    """
    if not value:
        return ""
    
    length = len(value)
    
    if length <= visible_start + visible_end:
        return mask_char * 3
    
    start = value[:visible_start]
    end = value[-visible_end:]
    masked = mask_char * 3
    
    return f"{start}{masked}{end}"

def determine_severity(risk_level: str, entropy: float = None) -> str:
    """
    Конвертирует RiskLevel в severity для API
    """
    mapping = {
        "high": "critical" if entropy and entropy > 4.5 else "high",
        "medium": "medium",
        "low": "low"
    }
    return mapping.get(risk_level, "low")