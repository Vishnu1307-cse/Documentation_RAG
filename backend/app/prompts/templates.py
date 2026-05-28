# System instructions enforcing senior architect persona
SYSTEM_INSTRUCTION = (
    "You are a Senior Software Architect and Technical Writer.\n"
    "Your task is to analyze the provided code context snippets retrieved from a repository "
    "and generate highly professional, accurate, and comprehensive documentation for a specific section.\n"
    "Follow these absolute guidelines:\n"
    "1. Rely ONLY on the code snippets in the Context. If you cannot find relevant details, state that it is not visible or not implemented in the analyzed portion.\n"
    "2. DO NOT make assumptions or hallucinate functions, endpoints, or technologies not present in the code.\n"
    "3. Format your response strictly in clean Markdown with clear headings.\n"
    "4. Highlight security patterns, potential vulnerabilities, and design patterns explicitly in the code you examine."
)

# Individual section prompts formatted using .format()
OVERVIEW_PROMPT = (
    "Generate a 'Project Overview' section for the codebase based on the context below.\n"
    "Explain:\n"
    "- The primary purpose of this project\n"
    "- Key technologies, languages, frameworks, or third-party packages used\n"
    "- High-level architectural patterns visible\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '1. Project Overview' (Markdown heading, no extra wrapper notes):"
)

FOLDER_PROMPT = (
    "Generate a 'Folder Structure & Responsibilities' section for the codebase based on the context below.\n"
    "Identify:\n"
    "- The primary directories and files\n"
    "- The exact responsibility or role of each folder/module in the codebase\n"
    "- How modules organize and reference each other\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '2. Folder Structure' (Markdown heading, no extra wrapper notes):"
)

ARCHITECTURE_PROMPT = (
    "Generate an 'Architecture & Design' section for the codebase based on the context below.\n"
    "Analyze:\n"
    "- The design patterns used (e.g., Singleton, MVC, BFF, Repository, Factory)\n"
    "- Boundaries and separation of concerns between layers (e.g. backend, API, services, DB)\n"
    "- Integration protocols and inter-service communication paradigms\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '3. Architecture Design' (Markdown heading, no extra wrapper notes):"
)

AUTH_PROMPT = (
    "Generate an 'Authentication & Session System' section for the codebase based on the context below.\n"
    "Describe:\n"
    "- How users or clients authenticate (e.g. JWT, cookies, OAuth, API keys)\n"
    "- Where and how credentials or tokens are validated on the server\n"
    "- Session management practices (timeouts, cookie flags like HttpOnly/Secure)\n"
    "- If no authentication is visible, clearly analyze where and how it should be securely integrated.\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '4. Authentication System' (Markdown heading, no extra wrapper notes):"
)

APIS_PROMPT = (
    "Generate an 'APIs, Routes & Middlewares' section for the codebase based on the context below.\n"
    "Document:\n"
    "- Available REST endpoints, GraphQL schemas, or routing trees\n"
    "- Inputs/parameters, HTTP verbs, response formats\n"
    "- Middleware intercepts (rate limiting, logging, security header policies, CORS checks)\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '5. APIs & Routes' (Markdown heading, no extra wrapper notes):"
)

DATABASE_PROMPT = (
    "Generate a 'Database Design & Models' section for the codebase based on the context below.\n"
    "Outline:\n"
    "- Data models, schema configurations, or tables found\n"
    "- Relationships (One-to-Many, Many-to-Many, etc.)\n"
    "- Database driver/ORM in use (e.g. SQLAlchemy, Mongoose, raw SQL)\n"
    "- Security of query creation (prepared statements, SQL injection mitigations)\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '6. Database Design' (Markdown heading, no extra wrapper notes):"
)

FLOW_PROMPT = (
    "Generate an 'Execution Flow & Request Lifecycle' section for the codebase based on the context below.\n"
    "Trace:\n"
    "- The chronological request lifecycle (e.g. from route reception, through middleware, controller, service layer, down to DB query, and back)\n"
    "- Key entrypoint files and launch execution flow\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '7. Execution Flow' (Markdown heading, no extra wrapper notes):"
)

IMPROVEMENTS_PROMPT = (
    "Generate a 'Potential Improvements & Hardening' section for the codebase based on the context below.\n"
    "Recommend:\n"
    "- Security hardening opportunities (e.g. unsafe string concat, missing CORS blocks, input sanitizations)\n"
    "- Scalability and performance enhancements (caching, background workers, query optimizations)\n"
    "- Maintenance and code design upgrades\n\n"
    "Context:\n"
    "{retrieved_context}\n\n"
    "Generate '8. Potential Improvements' (Markdown heading, no extra wrapper notes):"
)

# Dictionary of active prompt queries mapped to their respective sections
PROMPT_SECTIONS = {
    "1_overview": {"prompt": OVERVIEW_PROMPT, "query": "project architecture, technologies, frameworks, readme"},
    "2_folder": {"prompt": FOLDER_PROMPT, "query": "folder structure, directory organization, entry point files"},
    "3_architecture": {"prompt": ARCHITECTURE_PROMPT, "query": "design patterns, MVC, BFF, repository classes, services"},
    "4_auth": {"prompt": AUTH_PROMPT, "query": "authentication, token, jwt, session, password, login, secure path"},
    "5_apis": {"prompt": APIS_PROMPT, "query": "api endpoints, routes, router, request, controllers, middlewares"},
    "6_database": {"prompt": DATABASE_PROMPT, "query": "database schemas, model, sql query, relational, table"},
    "7_flow": {"prompt": FLOW_PROMPT, "query": "entrypoint launch, request lifecycle, application boot, main flow"},
    "8_improvements": {"prompt": IMPROVEMENTS_PROMPT, "query": "vulnerabilities, unsafe patterns, performance bottlenecks, issues"},
}
