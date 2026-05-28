import logging
import asyncio
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class JobState(BaseModel):
    job_id: str
    status: str  # pending | processing | complete | error
    progress_step: str  # e.g., "Cloning repository..."
    error_message: str | None = None
    github_url: str
    result_path: str | None = None

class JobManager:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(JobManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.jobs = {}
        return cls._instance

    async def create_job(self, job_id: str, github_url: str) -> JobState:
        """Initializes a new background tracking job entry."""
        async with self._lock:
            state = JobState(
                job_id=job_id,
                status="pending",
                progress_step="Job enqueued...",
                github_url=github_url
            )
            self.jobs[job_id] = state
            logger.info(f"Job state created: {job_id}")
            return state

    async def update_job(
        self,
        job_id: str,
        status: str = None,
        progress_step: str = None,
        error_message: str = None,
        result_path: str = None
    ) -> JobState | None:
        """Thread-safely updates the values of an existing job tracking state."""
        async with self._lock:
            if job_id not in self.jobs:
                logger.warning(f"Attempted to update non-existent job: {job_id}")
                return None
                
            state = self.jobs[job_id]
            if status:
                state.status = status
            if progress_step:
                state.progress_step = progress_step
            if error_message:
                state.error_message = error_message
            if result_path:
                state.result_path = result_path
                
            self.jobs[job_id] = state
            logger.info(f"Job state updated [{job_id}]: status={state.status}, step={state.progress_step}")
            return state

    async def get_job(self, job_id: str) -> JobState | None:
        """Retrieves details of a tracked job."""
        async with self._lock:
            return self.jobs.get(job_id)
