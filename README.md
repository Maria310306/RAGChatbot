# RAG Chatbot Backend

This is the backend implementation for an embedded Retrieval-Augmented Generation (RAG) chatbot for a published book.

## Overview

The RAG chatbot backend provides:
- Content ingestion and embedding storage
- Semantic retrieval from book content
- Dual query modes: global book RAG and selected-text-only
- Session management for conversations
- FastAPI-based REST API

## Tech Stack

- **Python 3.9+**
- **FastAPI** - Web framework
- **PostgreSQL** - Session and metadata storage (via Neon Serverless)
- **Qdrant** - Vector storage for embeddings
- **OpenAI** - LLM and embeddings
- **LangChain** - RAG orchestration
- **SQLAlchemy** - Database ORM

## Deployment

### Railway Deployment

This application is Docker-ready for easy deployment on Railway.

1. **Sign up to Railway**: Go to [railway.app](https://railway.app) and sign in with GitHub

2. **Create a new project**: Connect your GitHub repository

3. **Set environment variables** in Railway:
   - `POSTGRES_SERVER` - Your Neon project server URL
   - `POSTGRES_USER` - Database username
   - `POSTGRES_PASSWORD` - Database password
   - `POSTGRES_DB` - Database name
   - `QDRANT_HOST` - Your Qdrant cluster URL
   - `QDRANT_API_KEY` - Your Qdrant API key
   - `OPENAI_API_KEY` - Your OpenAI API key

4. **Deploy**: Railway will automatically build and deploy using the Dockerfile

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your configuration:
   ```env
   POSTGRES_SERVER=your_neon_server
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_database
   QDRANT_HOST=your_qdrant_host
   QDRANT_API_KEY=your_qdrant_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Set up the database tables (this happens automatically when the app starts)

## Running the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

API documentation is available at `http://localhost:8000/docs`.

## Required Environment Variables

Before running the application, you must set up the following environment variables:

### Database Configuration (Neon Serverless Postgres)
- `POSTGRES_SERVER`: Your Neon project server URL
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

### Qdrant Vector Database Configuration
- `QDRANT_HOST`: Your Qdrant cluster URL
- `QDRANT_API_KEY`: Your Qdrant API key

### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Configuration
- `DEBUG`: Set to "True" for development (default: "False")
- `HOST`: Host address (default: "0.0.0.0")
- `PORT`: Port number (default: 8000)

## Content Ingestion

To ingest book content into the system:

```bash
# For a single file
python ingest_content.py /path/to/your/book.txt --type file

# For a directory of files
python ingest_content.py /path/to/your/book/directory --type directory
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/chat` - Main chat endpoint
- `GET /api/v1/sessions` - Get all sessions
- `POST /api/v1/sessions` - Create a new session
- `GET /api/v1/sessions/{id}` - Get a specific session
- `PATCH /api/v1/sessions/{id}` - Update a session
- `DELETE /api/v1/sessions/{id}` - Delete a session
- `GET /api/v1/sessions/{id}/messages` - Get all messages for a session

## Query Modes

The system supports two query modes:

1. **Global book RAG** (default): Uses semantic search across the entire book content
2. **Selected-text-only**: Generates responses only from the provided selected text, ignoring the broader book context

To use selected-text-only mode, include the `mode` parameter as "selected_text_only" and provide the `selected_text`:

```json
{
  "query": "Your question here",
  "mode": "selected_text_only",
  "selected_text": "The text you want the AI to focus on"
}
```