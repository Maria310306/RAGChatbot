# Test script to validate the code structure without running the full application
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test that all modules can be imported without errors (ignoring config validation)"""
    errors = []
    
    try:
        # Test core modules
        import app.core.config
        print("[SUCCESS] Config module imported")
    except Exception as e:
        errors.append(f"Config module: {e}")
        
    try:
        # Test database modules
        import app.database.session
        print("[SUCCESS] Database session module imported")
    except Exception as e:
        errors.append(f"Database session module: {e}")
        
    try:
        # Test model modules
        from app.models import base, chat_session
        print("[SUCCESS] Model modules imported")
    except Exception as e:
        errors.append(f"Model modules: {e}")
        
    try:
        # Test schema modules
        import app.schemas.chat
        print("[SUCCESS] Schema module imported")
    except Exception as e:
        errors.append(f"Schema module: {e}")
        
    try:
        # Test utility modules
        import app.utils.vector_store
        print("[SUCCESS] Vector store utility module imported")
    except Exception as e:
        errors.append(f"Vector store utility module: {e}")
        
    try:
        # Test utility modules
        import app.utils.text_processing
        print("[SUCCESS] Text processing utility module imported")
    except Exception as e:
        errors.append(f"Text processing utility module: {e}")
        
    try:
        # Test RAG service
        import app.core.rag_service
        print("[SUCCESS] RAG service module imported")
    except Exception as e:
        errors.append(f"RAG service module: {e}")
        
    if errors:
        print("\n[ERRORS FOUND]:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n[SUCCESS] All modules imported successfully!")
        return True

if __name__ == "__main__":
    print("Testing RAG Chatbot Backend module imports...")
    success = test_imports()
    
    if success:
        print("\nThe backend structure is valid. To run the application:")
        print("1. Set up your environment variables (PostgreSQL, Qdrant, OpenAI credentials)")
        print("2. Run: python main.py")
        print("3. The API will be available at: http://localhost:8000")
    else:
        print("\nThere are issues with the backend code structure.")