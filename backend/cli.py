# cli.py (добавь эту функцию в начало)

from models.schemas import Rule, RiskLevel, SecretType

def create_test_rules():
    """Создает тестовые правила для сканирования"""
    return [
        Rule(
            name="AWS Access Key",
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
        Rule(
            name="API Key",
            pattern=r"(?i)(api[_-]?key|apikey|api_secret|api_token)[\s]*[:=][\s]*['\"]?([a-zA-Z0-9_\-]{16,64})['\"]?",
            risk_level=RiskLevel.MEDIUM,
            secret_type=SecretType.API_KEY,
            description="API ключи"
        ),
        Rule(
            name="Private Key",
            pattern=r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
            risk_level=RiskLevel.HIGH,
            secret_type=SecretType.PRIVATE_KEY,
            description="Приватный ключ"
        ),
        Rule(
            name="Password",
            pattern=r"(?i)(password|passwd|pwd)[\s]*[:=][\s]*['\"]?([^'\"]{8,})['\"]?",
            risk_level=RiskLevel.MEDIUM,
            secret_type=SecretType.PASSWORD,
            description="Пароль"
        ),
        Rule(
            name="JWT Token",
            pattern=r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
            risk_level=RiskLevel.HIGH,
            secret_type=SecretType.TOKEN,
            description="JWT токен"
        ),
    ]