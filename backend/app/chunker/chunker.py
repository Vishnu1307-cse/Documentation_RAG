import uuid
import logging
from pydantic import BaseModel
from app.parser.file_reader import FileRecord

logger = logging.getLogger(__name__)

class CodeChunk(BaseModel):
    chunk_id: str
    file_name: str
    relative_path: str
    language: str
    content: str
    char_start: int
    char_end: int

class CodeChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150, min_chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_file(self, record: FileRecord) -> list[CodeChunk]:
        """
        Splits file content into overlapping chunks recursively based on natural separators:
        1. Paragraphs / empty lines (double newlines)
        2. Lines (single newline)
        3. Spaces
        4. Characters (fallback)
        """
        content = record.content
        total_len = len(content)
        
        # If the file is small, keep it as a single chunk
        if total_len <= self.chunk_size:
            if total_len < self.min_chunk_size and total_len > 0:
                # Include tiny files if they are not completely empty
                pass
            return [
                CodeChunk(
                    chunk_id=str(uuid.uuid4()),
                    file_name=record.file_name,
                    relative_path=record.relative_path,
                    language=record.language,
                    content=content,
                    char_start=0,
                    char_end=total_len
                )
            ]

        chunks = []
        start = 0
        
        while start < total_len:
            end = min(start + self.chunk_size, total_len)
            
            # If we are not at the end of the file, try to find a natural split point
            if end < total_len:
                segment = content[start:end]
                
                # 1. Try splitting by double newline (class/function boundaries)
                split_idx = segment.rfind("\n\n")
                if split_idx != -1 and split_idx > self.chunk_size // 3:
                    end = start + split_idx
                else:
                    # 2. Try splitting by single newline (statement boundaries)
                    split_idx = segment.rfind("\n")
                    if split_idx != -1 and split_idx > self.chunk_size // 2:
                        end = start + split_idx
                    else:
                        # 3. Try splitting by space (word boundaries)
                        split_idx = segment.rfind(" ")
                        if split_idx != -1 and split_idx > self.chunk_size // 1.5:
                            end = start + split_idx
            
            chunk_content = content[start:end].strip()
            
            # Save chunk if it passes the size constraint
            if len(chunk_content) >= self.min_chunk_size:
                chunks.append(
                    CodeChunk(
                        chunk_id=str(uuid.uuid4()),
                        file_name=record.file_name,
                        relative_path=record.relative_path,
                        language=record.language,
                        content=chunk_content,
                        char_start=start,
                        char_end=end
                    )
                )
                
            # Slide window forward with overlap
            # Ensure we make forward progress to avoid infinite loop
            next_start = end - self.chunk_overlap
            if next_start <= start:
                start = end
            else:
                start = next_start
                
        return chunks

    def chunk_all(self, records: list[FileRecord]) -> list[CodeChunk]:
        """Processes all file records and generates a unified list of CodeChunks."""
        all_chunks = []
        for rec in records:
            all_chunks.extend(self.chunk_file(rec))
        logger.info(f"Generated {len(all_chunks)} chunks from {len(records)} files.")
        return all_chunks
