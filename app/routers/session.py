from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_async_db
from app.schemas.chat import ChatSession, ChatSessionCreate, ChatSessionUpdate, ChatSessionWithMessages, ChatMessage
from app.models.chat_session import ChatSession as ChatSessionModel, ChatMessage as ChatMessageModel

router = APIRouter()


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_session(session_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a specific chat session with its messages
    """
    try:
        result = await db.execute(
            ChatSessionModel.__table__.select().where(
                ChatSessionModel.id == session_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages_result = await db.execute(
            ChatMessageModel.__table__.select().where(
                ChatMessageModel.session_id == session_id
            ).order_by(ChatMessageModel.timestamp)
        )
        messages = messages_result.scalars().all()

        # Convert to Pydantic model
        session_data = ChatSessionWithMessages.from_orm(session)
        session_data.messages = messages

        return session_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.patch("/sessions/{session_id}", response_model=ChatSession)
async def update_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update a specific chat session
    """
    try:
        result = await db.execute(
            ChatSessionModel.__table__.select().where(
                ChatSessionModel.id == session_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update fields if they are provided
        if session_update.title is not None:
            session.title = session_update.title
        if session_update.is_active is not None:
            session.is_active = session_update.is_active

        await db.commit()
        await db.refresh(session)

        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a specific chat session
    """
    try:
        result = await db.execute(
            ChatSessionModel.__table__.select().where(
                ChatSessionModel.id == session_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        await db.delete(session)
        await db.commit()

        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(session_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve all messages for a specific session
    """
    try:
        messages_result = await db.execute(
            ChatMessageModel.__table__.select().where(
                ChatMessageModel.session_id == session_id
            ).order_by(ChatMessageModel.timestamp)
        )
        messages = messages_result.scalars().all()

        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session messages: {str(e)}")