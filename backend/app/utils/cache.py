import hashlib
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, job_id: str, ttl_seconds: int = 86400):
        self.job_id = job_id
        self.created_at = time.time()
        self.ttl = ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > (self.created_at + self.ttl)

class URLCache:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(URLCache, cls).__new__(cls, *args, **kwargs)
            cls._instance.store = {}
        return cls._instance

    def _hash_url(self, url: str) -> str:
        """Generates a secure SHA-256 hash representing the URL."""
        return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()

    async def get(self, url: str) -> str | None:
        """Retrieves non-expired job_id associated with a cached URL."""
        hashed = self._hash_url(url)
        async with self._lock:
            entry: CacheEntry | None = self.store.get(hashed)
            if entry:
                if entry.is_expired():
                    logger.info(f"Cache expired for hashed URL: {hashed}")
                    del self.store[hashed]
                    return None
                logger.info(f"Cache hit! Hashed URL: {hashed} -> Job ID: {entry.job_id}")
                return entry.job_id
            return None

    async def set(self, url: str, job_id: str, ttl_seconds: int = 86400) -> None:
        """Stores a job_id with the hashed URL."""
        hashed = self._hash_url(url)
        async with self._lock:
            self.store[hashed] = CacheEntry(job_id, ttl_seconds)
            logger.info(f"Cache stored for URL. Hashed: {hashed} -> Job: {job_id}")
