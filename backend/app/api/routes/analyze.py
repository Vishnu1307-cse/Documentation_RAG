import uuid
import logging
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.github.validator import validate_github_url
from app.utils.job_manager import JobManager
from app.tasks.processor import process_repository_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analyze"])

# Local rate limiter reference
limiter = Limiter(key_func=get_remote_address)

class AnalyzeRequest(BaseModel):
    github_url: str = Field(..., description="The standard cloneable URL of a public GitHub repository.")
    llm_provider: str = Field("openai", description="Active LLM Cloud provider: openai | anthropic | gemini | deepseek")

class AnalyzeResponse(BaseModel):
    job_id: str
    status: str
    message: str

ALLOWED_LLM_PROVIDERS = {"openai", "anthropic", "claude", "gemini", "google", "deepseek"}

@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/minute")
async def analyze_repository(
    request: Request,
    payload: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Submits a new public GitHub URL for deep RAG structured analysis.
    Starts processing in a non-blocking background job.
    """
    url = payload.github_url.strip()
    provider = payload.llm_provider.lower().strip()
    
    # 1. URL validation
    if not validate_github_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL. Must be formatted like: https://github.com/owner/repo"
        )
        
    # 2. Provider validation
    if provider not in ALLOWED_LLM_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported LLM provider: {payload.llm_provider}. Allowed: {list(ALLOWED_LLM_PROVIDERS)}"
        )
        
    # 3. Create UUID job tracker
    job_id = str(uuid.uuid4())
    job_manager = JobManager()
    await job_manager.create_job(job_id=job_id, github_url=url)
    
    # 4. Dispatch async processing pipeline
    logger.info(f"Dispatching background analysis for job {job_id} on {url} via {provider}...")
    background_tasks.add_task(
        process_repository_pipeline,
        job_id=job_id,
        github_url=url,
        llm_provider=provider
    )
    
    return AnalyzeResponse(
        job_id=job_id,
        status="pending",
        message="Analysis job enqueued successfully."
    )
