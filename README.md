# Financial Document Management System

A production-ready FastAPI-based system with semantic search using AI/ML.
It allows organizations to upload, manage, analyze, and retrieve financial documents such as invoices, reports, and contracts.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (with SQLite fallback for local dev) via SQLAlchemy/Alembic
- **Vector DB:** ChromaDB
- **Authentication:** JWT-based
- **AI/ML:** LangChain, HuggingFace embeddings (`all-MiniLM-L6-v2`), Cross-Encoder Reranking (`ms-marco-MiniLM-L-6-v2`)
- **File Storage:** Local Directory

## Features
- **User Authentication & Authorization:** JWT and RBAC (Admin, Financial Analyst, Auditor, Client)
- **Document Management:** Upload, Retrieve, Search by metadata, Delete
- **RAG & Semantic Search:** Document chunking, vector embeddings, and highly accurate top-k semantic search using Cross-Encoder reranking.

## Running the Application Locally (Without Docker)
1. Setup Python environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run database migrations (defaults to local SQLite `sql_app.db`):
   ```bash
   alembic upgrade head
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running with Docker Compose
1. Ensure Docker is installed.
2. Run:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

## API Documentation
The API docs are automatically generated via FastAPI and can be found at `/docs` (Swagger UI).
A Postman collection is also provided: `postman_collection.json`.
