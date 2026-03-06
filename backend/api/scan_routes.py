from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import Annotated
import uuid

from services.file_handler import FileHandler
from services.report_generator import ReportGenerator
from models.schemas import ScanResult, ScanSummary, Finding, Recommendation

router = APIRouter(prefix="/api/scan", tags=["Scanning"])
file_handler = FileHandler()

# Наша In-Memory база данных
scans_store: dict[str, ScanResult] = {}

# Используем Annotated - это современный стандарт FastAPI
@router.post("/")
async def upload_and_scan(file: Annotated[UploadFile, File(description="ZIP archive with source code")]):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")
    
    scan_id = str(uuid.uuid4())[:8]
    zip_content = await file.read()
    
    # 1. Распаковываем
    extracted_dir = file_handler.extract_zip(zip_content, scan_id)
    
    # 2. Собираем список файлов
    files_to_scan = file_handler.collect_files(extracted_dir)
    
    # ========================================================
    # ⚠️ ИНТЕГРАЦИЯ С УЧАСТНИКОМ 2 БУДЕТ ЗДЕСЬ ⚠️
    # Когда его код будет готов, ты заменишь фейковые данные ниже на:
    # 
    # from core.scanner_engine import ScannerEngine
    # scanner = ScannerEngine()
    # actual_findings = scanner.scan_files(files_to_scan)
    # ========================================================
    
    # ФЕЙКОВЫЕ ДАННЫЕ (Пока Участник 2 пишет сканер)
    mock_finding = Finding(
        id=1,
        file_path="src/config/db.py",
        line_number=12,
        secret_type="Database Connection String",
        severity="critical",
        matched_value="postgres://admin:****@localhost",
        recommendation=Recommendation(
            title="Вынесите строку подключения в .env",
            problem="Пароль хранится в открытом виде",
            solution="Используйте переменные окружения",
            code_example="DB_URL = os.getenv('DATABASE_URL')"
        )
    )
    
    result = ScanResult(
        scan_id=scan_id,
        status="completed",
        project_name=file.filename,
        summary=ScanSummary(
            total_files_scanned=len(files_to_scan),
            total_findings=1,
            by_severity={"critical": 1, "high": 0, "medium": 0, "low": 0}
        ),
        findings=[mock_finding] # <-- Позже заменишь на actual_findings
    )
    
    # 3. Сохраняем в память
    scans_store[scan_id] = result
    
    # 4. (Опционально) Очищаем временную папку
    # file_handler.cleanup(scan_id)
    
    return {"scan_id": scan_id, "status": "completed"}

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
    
    # В FastAPI > 0.100 Pydantic V2 автоматически сериализуется
    return result