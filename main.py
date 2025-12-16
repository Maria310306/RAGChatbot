from fastapi import FastAPI
from app.routers import chat, session
from app.core.config import settings
import uvicorn
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine

# Import models to register them with SQLAlchemy
from app.models import chat_session

# Import base for table creation
from app.models.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Embedded RAG Chatbot for Published Book",
    lifespan=lifespan
)

# Include API routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(session.router, prefix="/api/v1", tags=["session"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Embedded RAG Chatbot API",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )