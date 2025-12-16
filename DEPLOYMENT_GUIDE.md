# Deployment Guide for RAG Chatbot Backend

## Prerequisites

Before deploying the RAG Chatbot backend, ensure you have the following:

- Python 3.9 or higher
- PostgreSQL database (e.g., Neon Serverless Postgres)
- Qdrant Cloud account (or self-hosted Qdrant instance)
- OpenAI API key
- Docker (optional, for containerized deployment)

## Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RAGChatbotBackend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file:
   ```env
   POSTGRES_SERVER=your-neon-project.region.provider.neon.tech
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_database_name
   QDRANT_HOST=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   OPENAI_API_KEY=your_openai_api_key
   DEBUG=False
   HOST=0.0.0.0
   PORT=8000
   ```

## Database Setup

1. The application will automatically create required tables when started, using SQLAlchemy models.

2. Ensure your PostgreSQL database is accessible with the credentials provided in the environment variables.

## Content Ingestion

Before using the chatbot, you need to ingest your book content:

1. Prepare your book content in text format (TXT or Markdown files).

2. Run the ingestion script:
   ```bash
   # For a single file
   python ingest_content.py /path/to/your/book.txt --type file

   # For a directory of files
   python ingest_content.py /path/to/your/book/directory --type directory
   ```

## Running the Application

### Development Mode
```bash
python main.py
```

### Production Mode with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker
1. Create a Dockerfile:
   ```Dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Build the image:
   ```bash
   docker build -t rag-chatbot-backend .
   ```

3. Run the container:
   ```bash
   docker run -d -p 8000:8000 --env-file .env rag-chatbot-backend
   ```

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- `http://<your-server>:8000/docs` - Interactive API documentation (Swagger UI)
- `http://<your-server>:8000/redoc` - Alternative API documentation (ReDoc)

## Monitoring and Logging

The application logs to stdout by default. For production deployments, configure your server to capture and store logs appropriately.

Health check endpoint: `GET /health`

## Scaling Considerations

1. **Database Scaling**: Ensure your PostgreSQL instance can handle the expected load.
2. **Vector Database**: Monitor Qdrant performance and scale accordingly.
3. **API Scaling**: Use multiple workers when running with Uvicorn for better concurrency.
4. **Caching**: Consider implementing Redis or another caching layer for frequently requested content.

## Security Considerations

1. Keep API keys secure and never commit them to the repository.
2. Use HTTPS in production.
3. Implement rate limiting at the infrastructure level.
4. Consider implementing user authentication if needed for your use case.

## Troubleshooting

1. **Database Connection Issues**: Verify your PostgreSQL credentials and network access.
2. **Qdrant Connection Issues**: Check your Qdrant host and API key.
3. **OpenAI API Issues**: Verify your OpenAI API key and check for rate limits.
4. **Performance Issues**: Check your vector database indexing and ensure content is properly chunked.

## Updating the Application

1. Pull the latest code changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies if needed:
   ```bash
   pip install -r requirements.txt
   ```

3. Restart the application:
   ```bash
   # If running directly
   pkill -f "uvicorn\|python main.py"
   python main.py

   # If running in Docker
   docker stop <container-id>
   docker run -d -p 8000:8000 --env-file .env rag-chatbot-backend
   ```