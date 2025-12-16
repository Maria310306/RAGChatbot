from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Project information
    PROJECT_NAME: str = "Embedded RAG Chatbot for Published Book"
    VERSION: str = "1.0.0"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Database configurations
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Qdrant configuration
    QDRANT_HOST: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "book_content_embeddings"

    # OpenAI configuration
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    GPT_MODEL: str = "gpt-3.5-turbo"

    # Application settings
    MAX_CONTEXT_LENGTH: int = 3000  # Maximum length of context to send to LLM
    SIMILARITY_THRESHOLD: float = 0.7  # Minimum similarity score for retrieved results
    CHUNK_SIZE: int = 500  # Size of text chunks for embedding
    CHUNK_OVERLAP: int = 50  # Overlap between chunks

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


settings = Settings()