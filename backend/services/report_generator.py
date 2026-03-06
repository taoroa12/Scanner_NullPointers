import csv
import io
from models.schemas import ScanResult

class ReportGenerator:
    @staticmethod
    def generate_csv(scan_result: ScanResult) -> str:
        """Создает CSV в оперативной памяти."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["ID", "File Path", "Line Number", "Secret Type", "Severity", "Matched Value", "Recommendation"])
        
        for finding in scan_result.findings:
            writer.writerow([
                finding.id,
                finding.file_path,
                finding.line_number,
                finding.secret_type,
                finding.severity,
                finding.matched_value,
                finding.recommendation.title
            ])
            
        return output.getvalue()