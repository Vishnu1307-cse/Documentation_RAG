# Mapping of file extensions to programming language names
# Used for enrichments and RAG formatting prompts.
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "react_jsx",
    ".tsx": "react_tsx",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c_header",
    ".hpp": "cpp_header",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".sh": "bash",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
}

def detect_language(file_extension: str) -> str:
    """
    Returns the programming language name associated with the extension.
    Defaults to 'text' if not recognized.
    """
    ext = file_extension.lower().strip()
    # Normalize leading dot
    if ext and not ext.startswith("."):
        ext = f".{ext}"
    return EXTENSION_MAP.get(ext, "text")
