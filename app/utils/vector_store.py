import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class VectorStoreManager:
    def __init__(self):
        self.client = None
        self.embeddings = None
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._initialized = False

    def initialize(self):
        """Initialize the Qdrant client and embeddings - call this when needed"""
        if not self._initialized:
            self.client = QdrantClient(
                url=settings.QDRANT_HOST,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=True
            )
            self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
            self._ensure_collection_exists()
            self._initialized = True

    def _ensure_collection_exists(self):
        """Check if the collection exists, create if it doesn't"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception as e:
            # Only create the collection if it doesn't exist
            # Handle specific "collection exists" error
            if "already exists" not in str(e).lower() and "exists" not in str(e).lower():
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # Standard size for OpenAI embeddings
                        distance=models.Distance.COSINE
                    ),
                )

    def add_texts(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ) -> List[str]:
        """
        Add texts to the vector store

        Args:
            texts: List of texts to embed and store
            metadatas: Metadata for each text
            ids: IDs for each text (optional, will generate UUIDs if not provided)

        Returns:
            List of IDs of the added texts
        """
        self.initialize()  # Ensure client is initialized

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]

        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Generate embeddings
        embeddings = self.embeddings.embed_documents(texts)

        # Prepare points for insertion
        points = [
            models.PointStruct(
                id=id_,
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": metadata
                }
            )
            for id_, embedding, text, metadata in zip(ids, embeddings, texts, metadatas)
        ]

        # Insert into Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_condition: models.Filter = None
    ) -> List[Document]:
        """
        Perform similarity search in the vector store

        Args:
            query: Query text to search for
            k: Number of results to return
            filter_condition: Optional filter condition for search

        Returns:
            List of Documents matching the query
        """
        self.initialize()  # Ensure client is initialized

        query_embedding = self.embeddings.embed_query(query)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=k,
            query_filter=filter_condition,
            score_threshold=settings.SIMILARITY_THRESHOLD
        )

        documents = []
        for result in results:
            if result.score >= settings.SIMILARITY_THRESHOLD:
                doc = Document(
                    page_content=result.payload["text"],
                    metadata=result.payload["metadata"]
                )
                documents.append(doc)

        return documents

    def delete_collection(self):
        """Delete the entire collection (use with caution)"""
        self.initialize()  # Ensure client is initialized
        self.client.delete_collection(collection_name=self.collection_name)


# Global instance (not initialized at import time)
vector_store_manager = VectorStoreManager()