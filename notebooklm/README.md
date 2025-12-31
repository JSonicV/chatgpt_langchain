# NotebookLM Materials Index

This folder contains project-level documentation meant for NotebookLM ingestion.
Each file is self-contained and includes a purpose summary, flow description,
key code snippets, and how-to recipes.

## Projects

- `notebooklm/01_project.md` - LangChain code + test generator (CLI)
- `notebooklm/02_tchat.md` - CLI chat with LangChain memory
- `notebooklm/03_facts.md` - Facts embeddings + retrieval (Chroma)
- `notebooklm/04_agents.md` - SQL agent + reporting tools
- `notebooklm/05_pdf_backend.md` - Flask API + Celery + LangChain backend
- `notebooklm/05_pdf_frontend.md` - SvelteKit client + stores + chat UI

## Supplemental (non-code)

- `introduction.txt` - Course intro transcript about LangChain concepts
- `01_project/chatgpt_langchain_integration.txt` - Lecture transcript

## Notes

- All snippets are taken from source files and trimmed to the minimum needed.
- Environment variables are listed in each project file.
- If you only need a specific feature (auth, chat, embeddings), ingest the
  relevant project file instead of everything.
