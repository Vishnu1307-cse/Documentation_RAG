from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Simple status check verifying the backend services are operational."""
    return {"status": "ok", "message": "GitHub RAG backend running smoothly"}
