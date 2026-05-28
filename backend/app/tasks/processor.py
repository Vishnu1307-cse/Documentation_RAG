import logging
import traceback
from app.github.cloner import clone_repository, cleanup_repository
from app.parser.file_reader import traverse_and_read_repository
from app.chunker.chunker import CodeChunker
from app.embeddings.embedder import CodeEmbedder
from app.vectorstore.chroma_store import ChromaStore
from app.docs.generator import generate_documentation
from app.utils.job_manager import JobManager

logger = logging.getLogger(__name__)

async def process_repository_pipeline(job_id: str, github_url: str, llm_provider: str) -> None:
    """
    Asynchronous background job executing the RAG documentation pipeline.
    Steps:
      1. Clone Repository (Shallow)
      2. File Parsing & Sanitization
      3. Code base Chunking
      4. Embedding Generation
      5. ChromaDB upserts
      6. Structured Section Completions via Cloud LLM
      7. Safe filesystem cleaning of temporary workspace files
    """
    job_manager = JobManager()
    chroma_store = ChromaStore()
    
    logger.info(f"Background task pipeline initiated for job {job_id} ({github_url})")
    
    try:
        # Step 1: Clone
        await job_manager.update_job(job_id, status="processing", progress_step="Cloning repository...")
        repo_path = clone_repository(github_url, job_id)
        
        # Step 2: Parse
        await job_manager.update_job(job_id, progress_step="Parsing source files...")
        file_records = traverse_and_read_repository(repo_path)
        
        if not file_records:
            raise ValueError("No supported text/code files found in the repository.")
            
        # Step 3: Chunk
        await job_manager.update_job(job_id, progress_step="Segmenting files into chunks...")
        chunker = CodeChunker()
        chunks = chunker.chunk_all(file_records)
        
        if not chunks:
            raise ValueError("No viable semantic chunks generated from parsed files.")
            
        # Step 4: Embed
        await job_manager.update_job(job_id, progress_step="Generating semantic embeddings...")
        embedder = CodeEmbedder()
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Step 5: Load vectors to db
        await job_manager.update_job(job_id, progress_step="Indexing chunks into vector database...")
        chroma_store.upsert_chunks(
            job_id=job_id,
            chunks=chunks,
            embeddings=embeddings
        )
        
        # Step 6: Generate structured documentation via Cloud LLM
        await job_manager.update_job(job_id, progress_step="Generating structured architectural documentation...")
        result_file = await generate_documentation(job_id, llm_provider)
        
        # Step 7: Completed
        await job_manager.update_job(
            job_id=job_id,
            status="complete",
            progress_step="Documentation successfully generated!",
            result_path=str(result_file)
        )
        
    except Exception as e:
        logger.error(f"Error occurred in job pipeline {job_id}: {e}")
        logger.error(traceback.format_exc())
        
        await job_manager.update_job(
            job_id=job_id,
            status="error",
            progress_step="Failed due to an execution error.",
            error_message=str(e)
        )
        
    finally:
        # Step 8: Clean up raw cloned directory to reclaim space
        logger.info(f"Triggering cleanup for job workspace {job_id}...")
        cleanup_repository(job_id)
        
        # Clean up ChromaDB collection to prevent bloated storage
        logger.info(f"Triggering ChromaDB collection deletion for job {job_id}...")
        chroma_store.delete_job_collection(job_id)
