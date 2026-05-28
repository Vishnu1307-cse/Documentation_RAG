import re
import logging

logger = logging.getLogger(__name__)

# Strict regular expression to match standard GitHub HTTP(S) clone URLs
# Format: https://github.com/owner/repo or https://github.com/owner/repo.git
# Allows letters, digits, dashes, underscores, and periods in owner/repo names
GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?$"
)

def validate_github_url(url: str) -> bool:
    """
    Validates the format of a GitHub URL using a strict regex pattern.
    Rejects any inputs that might contain parameter injection or traversal structures.
    """
    if not url:
        return False
    
    # Strip whitespace
    url = url.strip()
    
    # Verify exact match
    match = GITHUB_URL_PATTERN.match(url)
    if not match:
        logger.warning(f"URL failed regex validation: {url}")
        return False
        
    owner, repo = match.groups()
    
    # Double check no directory traversal markers in the parts
    if ".." in owner or ".." in repo or "/" in owner or "/" in repo:
        logger.warning(f"URL contains path injection patterns: {url}")
        return False
        
    return True
