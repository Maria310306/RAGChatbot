import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.database.session import Base
from app.models.chat_session import ChatSession, ChatMessage


# Create a temporary in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the database session for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[app.router.dependencies[0]] = lambda: override_get_db()

# Create the testing client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "project" in data


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_session():
    """Test creating a new chat session"""
    session_data = {
        "title": "Test Session",
        "user_id": "test_user",
        "is_active": True
    }
    response = client.post("/api/v1/sessions", json=session_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == session_data["title"]
    assert data["user_id"] == session_data["user_id"]
    assert data["is_active"] == session_data["is_active"]


def test_get_sessions():
    """Test retrieving all chat sessions"""
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@patch("app.core.rag_service.rag_service.process_query")
def test_chat_endpoint(mock_rag_process):
    """Test the chat endpoint with mocked RAG service"""
    # Mock the RAG service response
    mock_rag_process.return_value = {
        "response": "This is a test response from the RAG service.",
        "sources": ["source1", "source2"],
        "session_id": 1
    }
    
    chat_data = {
        "query": "What is the meaning of life?",
        "mode": "global"
    }
    
    response = client.post("/api/v1/chat", json=chat_data)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "session_id" in data
    assert data["response"] == "This is a test response from the RAG service."


@patch("app.core.rag_service.rag_service.process_query")
def test_chat_endpoint_selected_text_mode(mock_rag_process):
    """Test the chat endpoint in selected-text-only mode"""
    # Mock the RAG service response
    mock_rag_process.return_value = {
        "response": "This is a response based only on the selected text.",
        "sources": ["selected_text"],
        "session_id": 1
    }
    
    chat_data = {
        "query": "What does this selected text mean?",
        "mode": "selected_text_only",
        "selected_text": "This is the selected text that the response should be based on."
    }
    
    response = client.post("/api/v1/chat", json=chat_data)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "session_id" in data
    assert data["response"] == "This is a response based only on the selected text."


def test_get_session_messages():
    """Test retrieving messages for a specific session"""
    # First create a session
    session_data = {
        "title": "Test Session for Messages",
        "user_id": "test_user",
        "is_active": True
    }
    session_response = client.post("/api/v1/sessions", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]
    
    # Then get messages for this session
    response = client.get(f"/api/v1/sessions/{session_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_session():
    """Test updating a session"""
    # First create a session
    session_data = {
        "title": "Test Session to Update",
        "user_id": "test_user",
        "is_active": True
    }
    session_response = client.post("/api/v1/sessions", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]
    
    # Then update the session
    update_data = {
        "title": "Updated Test Session",
        "is_active": False
    }
    response = client.patch(f"/api/v1/sessions/{session_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["is_active"] == update_data["is_active"]


def test_get_specific_session():
    """Test retrieving a specific session with its messages"""
    # First create a session
    session_data = {
        "title": "Test Session to Retrieve",
        "user_id": "test_user",
        "is_active": True
    }
    session_response = client.post("/api/v1/sessions", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]
    
    # Then get the specific session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == session_data["title"]
    assert data["user_id"] == session_data["user_id"]
    assert data["is_active"] == session_data["is_active"]
    assert "messages" in data
    assert isinstance(data["messages"], list)


def test_delete_session():
    """Test deleting a session"""
    # First create a session
    session_data = {
        "title": "Test Session to Delete",
        "user_id": "test_user",
        "is_active": True
    }
    session_response = client.post("/api/v1/sessions", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]
    
    # Then delete the session
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    # Verify the session is gone by trying to retrieve it
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404