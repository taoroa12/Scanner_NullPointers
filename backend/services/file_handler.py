import os
import zipfile
import tempfile
import shutil

class FileHandler:
    # Директории, которые мы пропускаем для ускорения
    EXCLUDED_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', '.idea', 'dist', 'build'}

    def __init__(self):
        # Создаем временную директорию ОС
        self.base_temp_dir = tempfile.mkdtemp(prefix="secret_scanner_")

    def is_binary(self, file_path: str) -> bool:
        """Эвристическая проверка: если в первых 1024 байтах есть нулевой байт, это бинарник."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk: 
                    return True
        except Exception:
            return True
        return False

    def extract_zip(self, zip_content: bytes, scan_id: str) -> str:
        """Распаковка ZIP в уникальную временную папку."""
        extract_path = os.path.join(self.base_temp_dir, scan_id)
        os.makedirs(extract_path, exist_ok=True)
        
        temp_zip_path = os.path.join(self.base_temp_dir, f"{scan_id}.zip")
        with open(temp_zip_path, 'wb') as f:
            f.write(zip_content)
            
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        os.remove(temp_zip_path) # Удаляем исходный архив
        return extract_path

    def collect_files(self, root_dir: str) -> list[str]:
        """Сбор всех путей к текстовым файлам (коду)."""
        files_to_scan = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Модифицируем список dirnames, чтобы os.walk не заходил в исключенные папки
            dirnames[:] = [d for d in dirnames if d not in self.EXCLUDED_DIRS]
            
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if not self.is_binary(file_path):
                    files_to_scan.append(file_path)
                    
        return files_to_scan

    def cleanup(self, scan_id: str):
        """Удаление файлов после сканирования."""
        path = os.path.join(self.base_temp_dir, scan_id)
        if os.path.exists(path):
            shutil.rmtree(path)

    def get_supported_extensions(self):
        """Возвращает список поддерживаемых расширений"""
        return [
            '.py', '.js', '.jsx', '.ts', '.tsx',
            '.yaml', '.yml', '.json', '.xml', '.toml', '.ini', '.conf',
            '.env', '.properties',
            '.md', '.txt',
            '.go', '.java', '.php', '.rb', '.rs', '.c', '.cpp', '.h',
            '.sh', '.bash', '.zsh', '.fish', '.ps1',
            '.sql',
            '.dockerfile', '.Dockerfile',
            '.gitignore', '.gitconfig',
            '.html', '.css', '.scss',
            '.tf', '.tfvars',
            '.rb', '.rake',
            '.swift', '.kt'
        ]