from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatSession, ChatSessionCreate, ChatMessage
from app.models.chat_session import ChatSession as ChatSessionModel, ChatMessage as ChatMessageModel
from app.core.rag_service import rag_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint that processes user queries using RAG
    """
    try:
        # Process the query using the RAG service
        result = rag_service.process_query(chat_request)
        
        # If session_id is provided, save the interaction to the database
        if chat_request.session_id:
            # Verify session exists
            session = db.query(ChatSessionModel).filter(
                ChatSessionModel.id == chat_request.session_id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Save user message
            user_message = ChatMessageModel(
                session_id=chat_request.session_id,
                role="user",
                content=chat_request.query
            )
            db.add(user_message)
            
            # Save assistant response
            assistant_message = ChatMessageModel(
                session_id=chat_request.session_id,
                role="assistant",
                content=result["response"]
            )
            db.add(assistant_message)
            
            db.commit()
        else:
            # Create a new session if none provided
            new_session = ChatSessionModel(
                title=chat_request.query[:50] + "..." if len(chat_request.query) > 50 else chat_request.query,
                user_id="anonymous"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            # Save user message
            user_message = ChatMessageModel(
                session_id=new_session.id,
                role="user",
                content=chat_request.query
            )
            db.add(user_message)
            
            # Save assistant response
            assistant_message = ChatMessageModel(
                session_id=new_session.id,
                role="assistant",
                content=result["response"]
            )
            db.add(assistant_message)
            
            db.commit()
            
            # Update the result to include the new session ID
            result["session_id"] = new_session.id
        
        # Include session_id in the response if not already present
        if "session_id" not in result:
            result["session_id"] = chat_request.session_id
        
        return ChatResponse(
            response=result["response"],
            sources=result.get("sources", []),
            session_id=result["session_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of chat sessions
    """
    try:
        sessions = db.query(ChatSessionModel).offset(skip).limit(limit).all()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")


@router.post("/sessions", response_model=ChatSession)
async def create_session(session: ChatSessionCreate, db: Session = Depends(get_db)):
    """
    Create a new chat session
    """
    try:
        db_session = ChatSessionModel(
            title=session.title,
            user_id=session.user_id,
            is_active=session.is_active
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")