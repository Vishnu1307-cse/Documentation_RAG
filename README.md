# GitHub Repository RAG Documentation System

A Python & React-based application that accepts a GitHub repository URL, downloads and processes it, chunks the code, stores its embeddings semantically in ChromaDB, and performs RAG (Retrieval-Augmented Generation) using Cloud LLM APIs to generate comprehensive structured documentation.

## Features
- **URL Validation**: Uses strict regular expressions to validate and filter input URLs.
- **Path Traversal Protection**: Employs absolute path resolution and sandbox prefix validation to guarantee code isolation.
- **Automatic Language Detection & Parsing**: Filter and read supported code files while ignoring junk and binary formats.
- **Recursive Chunking**: Smart dividing of large codebases into overlapping contextual snippets.
- **Local Embeddings**: Fast, CPU-friendly embedding generation via `sentence-transformers/all-MiniLM-L6-v2`.
- **Vector Database**: Semantic search query processing with ChromaDB.
- **Multi-Cloud LLM Integration**: Clean abstract provider factory supporting OpenAI, Claude (Anthropic), Gemini (Google), and DeepSeek.
- **Background Tasks**: Non-blocking asynchronous ingestion processing.
- **Beautiful Frontend**: Sleek React/Vite/TypeScript UI with responsive, stateful workflow animations, real-time status polling, and secure markdown viewer.

## Setup Instructions

### Backend
1. Python 3.11+ is required.
2. Navigate to `backend` directory.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and fill in the necessary cloud API keys:
   ```bash
   cp .env.example .env
   ```
6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. Navigate to `frontend` directory.
2. Install npm dependencies.
3. Start the local Vite server:
   ```bash
   npm run dev
   ```
