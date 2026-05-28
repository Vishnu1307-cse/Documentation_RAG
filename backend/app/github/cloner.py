import os
import shutil
import logging
import git
from pathlib import Path
from app.config import settings
from app.github.validator import validate_github_url

logger = logging.getLogger(__name__)

def get_directory_size(path: Path) -> int:
    """Returns directory size in bytes."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file(follow_symlinks=False):
            total += entry.stat(follow_symlinks=False).st_size
        elif entry.is_dir(follow_symlinks=False):
            total += get_directory_size(Path(entry.path))
    return total

def clone_repository(url: str, job_id: str) -> Path:
    """
    Clones a GitHub repository to a temporary directory inside the sandbox securely.
    Guarantees path containment and size limit validation.
    """
    if not validate_github_url(url):
        raise ValueError("Invalid GitHub repository URL format.")
    
    # 1. Establish and validate Sandbox Boundaries
    sandbox_path = Path(settings.SANDBOX_DIR).resolve()
    sandbox_prefix = str(sandbox_path) + os.sep
    
    # Ensure sandbox directory exists
    sandbox_path.mkdir(parents=True, exist_ok=True)
    
    # Define destination path based on random UUID job_id
    clone_dir = sandbox_path / job_id
    clone_dir_resolved = clone_dir.resolve()
    
    # Guarantee target folder is strictly inside the sandbox (Path Traversals prevention)
    # Check 1: String prefix starts with sandbox prefix (with trailing separator)
    if not str(clone_dir_resolved).startswith(sandbox_prefix):
        raise PermissionError("Path containment violation: Destination directory is outside the sandbox.")
    
    # Check 2: is_relative_to (Python 3.9+)
    try:
        if not clone_dir_resolved.is_relative_to(sandbox_path):
            raise PermissionError("Path containment violation: Destination directory is outside sandbox.")
    except AttributeError:
        # Fallback for older python, though Python 3.11+ is guaranteed
        pass

    # Ensure clean directory
    if clone_dir_resolved.exists():
        shutil.rmtree(clone_dir_resolved)
        
    logger.info(f"Cloning {url} to {clone_dir_resolved}...")
    
    try:
        # GitPython clone operation.
        # This does not execute raw shell commands, keeping command execution safe.
        git.Repo.clone_from(
            url=url.strip(),
            to_path=str(clone_dir_resolved),
            multi_options=["--depth=1"] # Fetch shallow clone to optimize performance and save space
        )
        
        # 2. Check Repository Size Limit
        size_bytes = get_directory_size(clone_dir_resolved)
        size_mb = size_bytes / (1024 * 1024)
        logger.info(f"Cloned size: {size_mb:.2f} MB")
        
        if size_mb > settings.MAX_REPO_SIZE_MB:
            logger.warning(f"Repository size {size_mb:.2f}MB exceeds limit of {settings.MAX_REPO_SIZE_MB}MB. Cleaning up...")
            cleanup_repository(job_id)
            raise ValueError(f"Repository size exceeds the maximum limit of {settings.MAX_REPO_SIZE_MB} MB.")
            
        return clone_dir_resolved
        
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        # Clean up in case of failure or partial clone
        if clone_dir_resolved.exists():
            shutil.rmtree(clone_dir_resolved)
        raise e

def cleanup_repository(job_id: str) -> None:
    """Removes the cloned repository directory from the sandbox."""
    if not job_id:
        return
        
    sandbox_path = Path(settings.SANDBOX_DIR).resolve()
    sandbox_prefix = str(sandbox_path) + os.sep
    
    target_dir = (sandbox_path / job_id).resolve()
    
    # Safety Check: Path must be within the sandbox before executing deletion
    if not str(target_dir).startswith(sandbox_prefix):
        logger.error(f"Refusing to delete directory outside sandbox: {target_dir}")
        return
        
    if target_dir.exists() and target_dir.is_dir():
        try:
            shutil.rmtree(target_dir)
            logger.info(f"Cleaned up directory: {target_dir}")
        except Exception as e:
            logger.error(f"Failed to delete directory {target_dir}: {e}")
