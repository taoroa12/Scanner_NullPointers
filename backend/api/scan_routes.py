from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import Annotated
import uuid
import os
from datetime import datetime

from services.file_handler import FileHandler
from services.report_generator import ReportGenerator
from services.rules_manager import RulesManager
from core.scanner_engine import SecretScanner
from core.severity import mask_secret, determine_severity
from models.schemas import ScanResult, ScanSummary, Finding, Recommendation

router = APIRouter(prefix="/api/scan", tags=["Scanning"])
file_handler = FileHandler()
rules_manager = RulesManager()

# Наша In-Memory база данных
scans_store: dict[str, ScanResult] = {}

# Убираем импорт из cli, добавляем тестовые правила прямо здесь
def get_test_rules():
    """Возвращает тестовые правила для отладки"""
    from models.schemas import Rule, RiskLevel, SecretType
    
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
            description="Пароль в конфигурационном файле"
        ),
        Rule(
            name="JWT Token",
            pattern=r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
            risk_level=RiskLevel.HIGH,
            secret_type=SecretType.TOKEN,
            description="JWT токен"
        ),
    ]

@router.post("/")
async def upload_and_scan(file: Annotated[UploadFile, File(description="ZIP archive with source code")]):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")
    
    scan_id = str(uuid.uuid4())[:8]
    zip_content = await file.read()
    
    try:
        # 1. Распаковываем
        extracted_dir = file_handler.extract_zip(zip_content, scan_id)
        
        # 2. Собираем список файлов
        files_to_scan = file_handler.collect_files(extracted_dir)
        
        # 3. Загружаем правила и создаем сканер
        rules = rules_manager.get_enabled_rules()
        if not rules:
            # Если нет правил, используем тестовые
            rules = get_test_rules()
            print("⚠️ Используются тестовые правила (YAML не найден)")
        
        scanner = SecretScanner(rules, use_entropy=True)
        
        # 4. Сканируем файлы
        extensions = file_handler.get_supported_extensions()
        findings_raw = scanner.scan_directory(extracted_dir, extensions=extensions)
        
        # 5. Загружаем рекомендации
        recommendations = rules_manager.get_recommendations()
        
        # 6. Конвертируем в формат API
                # 6. Конвертируем в формат API
        findings = []
        for i, f in enumerate(findings_raw, 1):
            
            # ДОСТАЕМ ДАННЫЕ ИЗ СЛОВАРЯ (через .get)
            rule_name = f.get('rule_name', 'Unknown')
            secret_type = f.get('secret_type', 'generic')
            risk_value = f.get('risk_level', 'medium')
            entropy = f.get('entropy', None)
            secret_masked = f.get('secret_masked', '***')
            file_path = f.get('file_path', 'unknown')
            line_number = f.get('line_number', 0)
            line_content = f.get('line_content', '')
            encoding_type = f.get('encoding_type', None)
            
            # Создаем базовую рекомендацию
            if rule_name in recommendations:
                rec_text = recommendations[rule_name]
                recommendation = Recommendation(
                    title=f"Рекомендация для {rule_name}",
                    problem="Обнаружен секрет в коде",
                    solution=rec_text[:200] if rec_text else "Используйте переменные окружения",
                    code_example="# Смотрите документацию по безопасности"
                )
            else:
                recommendation = Recommendation(
                    title=f"Удалите {rule_name} из кода",
                    problem=f"В файле найден {rule_name}. Это может привести к утечке данных.",
                    solution="Используйте переменные окружения (.env) или систему управления секретами (Vault).",
                    code_example=f"os.environ.get('{rule_name.upper().replace(' ', '_')}')"
                )
            
            # Собираем финальный объект Finding (ПЕРЕДАЕМ ВСЕ ПОЛЯ)
            finding = Finding(
                id=i,
                file_path=file_path,
                line_number=line_number,
                secret_type=secret_type,
                severity=determine_severity(risk_value, entropy),
                matched_value=secret_masked,
                recommendation=recommendation,
                entropy=entropy,
                encoding_type=encoding_type,
                rule_name=rule_name,
                line_content=line_content
            )
            findings.append(finding)
        
        # 7. Считаем статистику
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        
        result = ScanResult(
            scan_id=scan_id,
            status="completed",
            project_name=file.filename,
            summary=ScanSummary(
                total_files_scanned=len(files_to_scan),
                total_findings=len(findings),
                by_severity=by_severity
            ),
            findings=findings
        )
        
        # 8. Сохраняем в память
        scans_store[scan_id] = result
        
        # 9. Очищаем временную папку
        file_handler.cleanup(scan_id)
        
        print(f"✅ Сканирование завершено: {scan_id}, найдено {len(findings)} секретов")
        return {"scan_id": scan_id, "status": "completed", "findings_count": len(findings)}
        
    except Exception as e:
        # В случае ошибки тоже чистим
        file_handler.cleanup(scan_id)
        print(f"❌ Ошибка сканирования: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan_report(scan_id: str):
    """Возвращает готовый JSON отчет."""
    if scan_id not in scans_store:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans_store[scan_id]

@router.get("/{scan_id}/export")
async def export_report(scan_id: str, format: str = "json"):
    """Экспорт в CSV."""
    if scan_id not in scans_store:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    result = scans_store[scan_id]
    
    if format.lower() == "csv":
        csv_data = ReportGenerator.generate_csv(result)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{scan_id}.csv"}
        )
    
    return result