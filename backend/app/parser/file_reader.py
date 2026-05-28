import os
import logging
from pathlib import Path
from pydantic import BaseModel
import chardet
from app.parser.language_detector import detect_language

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp",
    ".go", ".rs", ".md", ".json", ".yaml", ".yml", ".html", ".css", ".sql"
}

# Directories to ignore
IGNORED_DIRECTORIES = {
    "node_modules", ".git", "dist", "build", "coverage", "__pycache__",
    "venv", ".venv", "env", ".env", "vendor", "images", "assets", "bin"
}

# Maximum single file size in bytes (500 KB)
MAX_FILE_SIZE_BYTES = 500 * 1024

class FileRecord(BaseModel):
    file_name: str
    relative_path: str
    language: str
    content: str
    size_bytes: int

def is_binary(file_path: Path) -> bool:
    """Detects if a file is binary by looking for null bytes in the first block."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True

def read_file_content(file_path: Path) -> str:
    """Reads content safely, attempting UTF-8 first then falling back to chardet detection."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except UnicodeDecodeError:
        # Read raw bytes and try fallback detection
        try:
            raw_bytes = file_path.read_bytes()
            detection = chardet.detect(raw_bytes[:10000])
            encoding = detection.get("encoding") or "utf-8"
            return raw_bytes.decode(encoding, errors="replace")
        except Exception as e:
            logger.warning(f"Failed to read file {file_path} with fallback encoding: {e}")
            raise e

def traverse_and_read_repository(repo_path: Path) -> list[FileRecord]:
    """
    Traverses the repository path recursively, filters, and reads file contents.
    Ensures path containment to prevent directory traversal escapes.
    """
    repo_path_resolved = repo_path.resolve()
    repo_prefix = str(repo_path_resolved) + os.sep
    
    file_records = []
    
    for root, dirs, files in os.walk(repo_path_resolved):
        # In-place modify dirs list to prune ignored directories from traversal
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        
        for file in files:
            file_path = Path(root) / file
            file_path_resolved = file_path.resolve()
            
            # 1. Path Containment check: File must reside inside repository path
            if not str(file_path_resolved).startswith(repo_prefix):
                logger.warning(f"Path containment violation: Skipping file outside repo boundary: {file_path_resolved}")
                continue
                
            # 2. Extension filter
            ext = file_path_resolved.suffix
            if ext not in ALLOWED_EXTENSIONS:
                continue
                
            # 3. File constraints: Ignore binary and check size limits
            try:
                stat = file_path_resolved.stat()
                if stat.st_size > MAX_FILE_SIZE_BYTES:
                    logger.warning(f"Skipping {file} - size {stat.st_size} bytes exceeds limit.")
                    continue
                    
                if is_binary(file_path_resolved):
                    continue
                    
                content = read_file_content(file_path_resolved)
                relative_path = os.path.relpath(file_path_resolved, repo_path_resolved)
                language = detect_language(ext)
                
                record = FileRecord(
                    file_name=file,
                    relative_path=relative_path,
                    language=language,
                    content=content,
                    size_bytes=stat.st_size
                )
                file_records.append(record)
                
            except Exception as e:
                logger.error(f"Error reading file {file_path_resolved}: {e}")
                continue
                
    logger.info(f"Traversed repository. Read {len(file_records)} files successfully.")
    return file_records
