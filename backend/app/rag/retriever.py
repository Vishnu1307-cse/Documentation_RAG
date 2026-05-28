import logging
from app.embeddings.embedder import CodeEmbedder
from app.vectorstore.chroma_store import ChromaStore

logger = logging.getLogger(__name__)

def retrieve_context(
    job_id: str,
    query: str,
    embedder: CodeEmbedder,
    chroma_store: ChromaStore,
    n_results: int = 6,
    max_context_chars: int = 15000
) -> str:
    """
    Retrieves semantically relevant code chunks from ChromaDB, formats them
    with clear metadata headers, and returns a single concatenated context string.
    Safely truncates outputs to avoid context-window bounds issues.
    """
    logger.info(f"Retrieving context for query: '{query}' (Job ID: {job_id})")
    
    # 1. Embed query text
    query_embedding = embedder.embed_query(query)
    
    # 2. Search ChromaDB
    chunks = chroma_store.query_similarity(
        job_id=job_id,
        query_embedding=query_embedding,
        n_results=n_results
    )
    
    if not chunks:
        logger.warning("No context chunks found or returned.")
        return "No relevant codebase context could be found for this query."
        
    context_blocks = []
    current_length = 0
    
    # 3. Format and concatenate retrieved snippets
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        path = meta.get("relative_path", "unknown_file")
        lang = meta.get("language", "text")
        content = chunk["content"]
        
        # Format block nicely with header indicators
        formatted_block = (
            f"--- Code Snippet #{i+1} ---\n"
            f"File: {path}\n"
            f"Language: {lang}\n"
            f"Content:\n"
            f"```\n"
            f"{content}\n"
            f"```\n\n"
        )
        
        block_len = len(formatted_block)
        
        # Enforce maximum character boundary limits to prevent LLM token-bound overflows
        if current_length + block_len > max_context_chars:
            logger.info(f"Context limits reached. Stopping retrieval after {i} chunks.")
            break
            
        context_blocks.append(formatted_block)
        current_length += block_len
        
    return "".join(context_blocks)
