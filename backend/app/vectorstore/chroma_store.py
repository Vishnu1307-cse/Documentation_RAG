import re
import logging
import chromadb
from app.config import settings
from app.chunker.chunker import CodeChunk

logger = logging.getLogger(__name__)

# Pattern to strictly validate the collection name to repo_<uuid> format
COLLECTION_NAME_PATTERN = re.compile(r"^repo_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")

class ChromaStore:
    def __init__(self):
        logger.info(f"Initializing ChromaDB persistent store at: {settings.CHROMA_DB_PATH}")
        try:
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        except Exception as e:
            logger.critical(f"Failed to initialize ChromaDB client: {e}")
            raise e

    def _get_collection_name(self, job_id: str) -> str:
        """Constructs and validates the collection name securely."""
        name = f"repo_{job_id}"
        if not COLLECTION_NAME_PATTERN.match(name):
            raise ValueError(f"Invalid characters or format in job_id: {job_id}")
        return name

    def upsert_chunks(self, job_id: str, chunks: list[CodeChunk], embeddings: list[list[float]]) -> None:
        """
        Stores chunk contents, embeddings, and metadata in a dedicated collection.
        Uses batching to handle large payloads efficiently.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Size mismatch: chunks and embeddings counts must be equal.")
            
        collection_name = self._get_collection_name(job_id)
        collection = self.client.get_or_create_collection(name=collection_name)
        
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "file_name": chunk.file_name,
                "relative_path": chunk.relative_path,
                "language": chunk.language,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end
            }
            for chunk in chunks
        ]
        
        # Batch size for ChromaDB insertions (typically 100-200 is optimal)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = i + batch_size
            collection.upsert(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
        logger.info(f"Successfully upserted {len(ids)} chunks to ChromaDB collection: {collection_name}")

    def query_similarity(self, job_id: str, query_embedding: list[float], n_results: int = 5) -> list[dict]:
        """
        Performs semantic vector similarity search against the collection.
        Returns a list of matching chunks with document body and metadata.
        """
        collection_name = self._get_collection_name(job_id)
        
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            logger.warning(f"Collection {collection_name} does not exist. Returning empty query results.")
            return []
            
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            # Deconstruct nested results returned by ChromaDB query
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            
            for i in range(len(docs)):
                formatted_results.append({
                    "chunk_id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i]
                })
                
        return formatted_results

    def delete_job_collection(self, job_id: str) -> None:
        """Deletes the collection associated with a job securely."""
        collection_name = self._get_collection_name(job_id)
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted ChromaDB collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection {collection_name}: {e}")
