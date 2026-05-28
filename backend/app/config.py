import os
import secrets
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env if present
load_dotenv()

def get_secret(key_name: str, required: bool = False) -> str:
    """
    Resolves secrets using a multi-tiered approach:
    1. Environment variables
    2. Local file query
    3. Error out or warn and fallback (depending on requirement)
    """
    # Tier 1: Environment
    val = os.getenv(key_name)
    if val:
        return val.strip()

    # Tier 2: Local File Query
    file_name = f"{key_name.lower()}.txt"
    file_path = Path(file_name)
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Failed to read secret from file {file_name}: {e}")

    # Tier 3: Fallback / Error
    if required:
        raise ValueError(f"CRITICAL: Secret '{key_name}' is not set in environment or file '{file_name}'!")
    
    # If not strictly required for startup but needed when requested, warn and return empty
    logger.warning(f"Secret '{key_name}' is not configured. APIs using this key will fail.")
    return ""

class Settings:
    # Server Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    
    # Strict CORS configuration
    raw_cors = os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:5173")
    ALLOWED_CORS_ORIGINS: list[str] = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
    
    # Application Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    SANDBOX_DIR: str = os.getenv("SANDBOX_DIR", "./temp_repos")
    GENERATED_DOCS_DIR: str = os.getenv("GENERATED_DOCS_DIR", "./generated_docs")
    
    # Constraints
    MAX_REPO_SIZE_MB: int = int(os.getenv("MAX_REPO_SIZE_MB", "50"))
    
    # Active LLM configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Models config
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # API Keys (Loaded dynamically via multi-tiered method)
    @property
    def openai_api_key(self) -> str:
        return get_secret("OPENAI_API_KEY")

    @property
    def anthropic_api_key(self) -> str:
        return get_secret("ANTHROPIC_API_KEY")

    @property
    def gemini_api_key(self) -> str:
        return get_secret("GEMINI_API_KEY")

    @property
    def deepseek_api_key(self) -> str:
        return get_secret("DEEPSEEK_API_KEY")

settings = Settings()
