import os
import logging
from pathlib import Path
from app.config import settings
from app.embeddings.embedder import CodeEmbedder
from app.vectorstore.chroma_store import ChromaStore
from app.rag.retriever import retrieve_context
from app.llm.provider_factory import LLMProviderFactory
from app.prompts.templates import SYSTEM_INSTRUCTION, PROMPT_SECTIONS

logger = logging.getLogger(__name__)

async def generate_documentation(job_id: str, provider_name: str) -> Path:
    """
    Orchestrates the retrieval and structured generation for all 8 documentation sections.
    Assembles a unified Markdown document and writes it securely to the sandboxed generated_docs dir.
    """
    logger.info(f"Starting structured documentation generation for job {job_id} using {provider_name}...")
    
    # Initialize tools and abstractions
    embedder = CodeEmbedder()
    chroma_store = ChromaStore()
    provider = LLMProviderFactory.get_provider(provider_name)
    
    markdown_sections = [
        f"# Technical Documentation: Codebase Analysis\n",
        f"*Generated automatically using RAG Semantic Search with {provider_name.upper()} Cloud LLM.*\n",
        f"**Job Identifier**: `{job_id}`\n\n",
        f"---\n\n"
    ]
    
    # Process each section sequentially to prevent rate limits or thread clashes
    for section_id, details in sorted(PROMPT_SECTIONS.items()):
        section_name = section_id.split("_")[1].capitalize()
        logger.info(f"Processing section: {section_name}...")
        
        # 1. Retrieve query-specific contextual snippets
        retrieved_context = retrieve_context(
            job_id=job_id,
            query=details["query"],
            embedder=embedder,
            chroma_store=chroma_store,
            n_results=5
        )
        
        # 2. Build the exact prompt payload
        prompt = details["prompt"].format(retrieved_context=retrieved_context)
        
        # 3. Request section completion from LLM provider
        try:
            section_content = provider.generate(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION
            )
            markdown_sections.append(section_content)
            markdown_sections.append("\n\n---\n\n")
        except Exception as e:
            logger.error(f"Failed to generate section {section_name}: {e}")
            markdown_sections.append(
                f"## {section_name}\n"
                f"*Error: Failed to generate this section via the cloud provider API.*"
            )
            markdown_sections.append("\n\n---\n\n")

    # Combine into a single string
    full_markdown = "".join(markdown_sections[:-1]) # Strip trailing separator

    # 4. Save file securely with strict path boundary check
    docs_dir = Path(settings.GENERATED_DOCS_DIR).resolve()
    docs_dir_prefix = str(docs_dir) + os.sep
    
    # Ensure directory exists safely
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = docs_dir / f"{job_id}.md"
    output_file_resolved = output_file.resolve()
    
    # Check path containment to prevent path traversal breakouts
    if not str(output_file_resolved).startswith(docs_dir_prefix):
        raise PermissionError("Path containment violation: Cannot write generated documentation outside safe sandbox.")
        
    logger.info(f"Saving completed technical documentation to: {output_file_resolved}")
    
    try:
        with open(output_file_resolved, "w", encoding="utf-8") as f:
            f.write(full_markdown)
    except Exception as e:
        logger.error(f"Failed to write documentation file to disk: {e}")
        raise e
        
    return output_file_resolved
