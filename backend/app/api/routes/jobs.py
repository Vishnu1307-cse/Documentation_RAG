import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response
from app.config import settings
from app.utils.job_manager import JobManager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Jobs"])

def validate_uuid(job_id: str) -> None:
    """Verifies that the job_id matches exactly a standard UUID format."""
    try:
        uuid.UUID(job_id)
    except ValueError:
        logger.warning(f"Malicious or malformed job_id parameter blocked: {job_id}")
        raise HTTPException(
            status_code=400,
            detail="Malformed job_id parameter format. UUID required."
        )

@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Retrieves the active state and chronological step status of a background job."""
    validate_uuid(job_id)
    
    job_manager = JobManager()
    state = await job_manager.get_job(job_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    return {
        "job_id": state.job_id,
        "status": state.status,
        "progress_step": state.progress_step,
        "error_message": state.error_message
    }

@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """
    Serves back the completed markdown documentation.
    Verifies path containment to restrict access to the generated docs sandboxed folder.
    """
    validate_uuid(job_id)
    
    job_manager = JobManager()
    state = await job_manager.get_job(job_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    if state.status != "complete" or not state.result_path:
        raise HTTPException(
            status_code=400,
            detail=f"Documentation is not available. Current job status: {state.status}"
        )
        
    result_path = Path(state.result_path).resolve()
    docs_dir = Path(settings.GENERATED_DOCS_DIR).resolve()
    docs_dir_prefix = str(docs_dir) + os.sep
    
    # Path containments check
    if not str(result_path).startswith(docs_dir_prefix):
        logger.error(f"Path containment breach blocked! Request path: {result_path}")
        raise HTTPException(
            status_code=403,
            detail="Forbidden path access attempt."
        )
        
    if not result_path.exists():
        logger.error(f"Target result file not found: {result_path}")
        raise HTTPException(status_code=404, detail="Documentation file not found on disk.")
        
    try:
        # Load and serve markdown content securely
        with open(result_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        return Response(content=markdown_content, media_type="text/markdown")
    except Exception as e:
        logger.error(f"Failed to read result file {result_path}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load generated documentation.")
