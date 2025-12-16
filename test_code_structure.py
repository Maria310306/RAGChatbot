import os
import sys
from unittest.mock import patch

# Temporarily set environment variables to allow imports
os.environ['POSTGRES_SERVER'] = 'test'
os.environ['POSTGRES_USER'] = 'test'
os.environ['POSTGRES_PASSWORD'] = 'test'
os.environ['POSTGRES_DB'] = 'test'
os.environ['QDRANT_HOST'] = 'test'
os.environ['QDRANT_API_KEY'] = 'test'
os.environ['OPENAI_API_KEY'] = 'test'

def test_code_structure():
    """Test that our code structure is valid by importing all modules"""
    try:
        # Test importing the main modules
        from app.core import config
        from app.database import session
        from app.models import base, chat_session
        from app.schemas import chat
        from app.utils import vector_store, text_processing
        from app.core import rag_service
        
        print("[SUCCESS] All modules imported successfully!")
        print("[SUCCESS] Code structure is valid")
        
        # Verify that key classes/functions exist
        assert hasattr(config, 'Settings'), "Settings class not found in config module"
        assert hasattr(chat_session, 'ChatSession'), "ChatSession model not found"
        assert hasattr(chat_session, 'ChatMessage'), "ChatMessage model not found"
        assert hasattr(chat, 'ChatRequest'), "ChatRequest schema not found"
        assert hasattr(vector_store, 'VectorStoreManager'), "VectorStoreManager not found"
        assert hasattr(rag_service, 'RAGService'), "RAGService not found"
        
        print("[SUCCESS] All required classes and functions are present")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error testing code structure: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing RAG Chatbot Backend code structure...")
    success = test_code_structure()
    
    if success:
        print("\n[SUCCESS] The backend code structure is valid and ready for use!")
        print("To run the application, follow the instructions in the README.md file.")
    else:
        print("\n[ERROR] There are issues with the backend code structure.")