import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class CodeEmbedder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CodeEmbedder, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        
        logger.info(f"Loading embedding model: {model_name}...")
        try:
            # CPU-friendly lightweight model
            self.model = SentenceTransformer(model_name)
            self._initialized = True
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load sentence transformer model: {e}")
            raise e

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generates semantic embeddings for a list of string texts.
        Returns a list of high-dimensional vectors (lists of floats).
        """
        if not texts:
            return []
            
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            # Convert numpy array to standard list of lists
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error during embedding generation: {e}")
            raise e

    def embed_query(self, query: str) -> list[float]:
        """Generates embedding vector for a single query string."""
        try:
            embedding = self.model.encode(query, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding search query: {e}")
            raise e
