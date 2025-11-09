from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.models.chat import Chat
from app.models.visitor import Visitor
from app.schemas.chat import ChatCreate, ChatOut
from app.core.database import get_db
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
from app.services.qdrant_service import search_similar_vectors
from app.services.openai_service import generate_reply
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.visitor import Visitor
from app.models.visitor_session import VisitorSession
from app.models.chatbot import Chatbot

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageIn(BaseModel):
    visitor_anonymous_id: str | None = None
    session_id: int | None = None
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{chatbot_id}/message")
def send_message(chatbot_id: int, payload: MessageIn, db: Session = Depends(get_db)):
    # locate chatbot
    chatbot = db.get(Chatbot, chatbot_id)
    if not chatbot:
        raise HTTPException(404, "Chatbot not found")

    # find or create VisitorSession — simplified
    if payload.session_id:
        session = db.get(VisitorSession, payload.session_id)
    else:
        # create new visitor and session (anonymous)
        from app.models.visitor import Visitor
        visitor = Visitor(anonymous_id=payload.visitor_anonymous_id or "anon-"+str(uuid.uuid4()))
        db.add(visitor); db.commit(); db.refresh(visitor)
        session = VisitorSession(visitor_id=visitor.id, chatbot_id=chatbot_id)
        db.add(session); db.commit(); db.refresh(session)

    # Save visitor message
    chat = Chat(visitor_session_id=session.id, chatbot_id=chatbot_id, role="visitor", message=payload.message)
    db.add(chat); db.commit(); db.refresh(chat)

    # TODO: call chatbot service / langchain -> generate bot response
    bot_text = "This is a placeholder response. Integrate Qdrant + LLM"

    bot_chat = Chat(visitor_session_id=session.id, chatbot_id=chatbot_id, role="bot", message=bot_text)
    db.add(bot_chat); db.commit()

    return {"reply": bot_text, "session_id": session.id}

@router.post("/", response_model=ChatOut)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    visitor = db.query(Visitor).filter(Visitor.id == chat.visitor_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    if datetime.utcnow() - visitor.created_at.replace(tzinfo=None) > timedelta(hours=1):
        raise HTTPException(status_code=410, detail="Session expired")

    db_chat = Chat(
        visitor_id=chat.visitor_id,
        chatbot_id=chat.chatbot_id,
        question=chat.question,
        answer="(GPT response will go here)",
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/visitor/{visitor_id}", response_model=List[ChatOut])
def get_visitor_chats(visitor_id: int, db: Session = Depends(get_db)):
    return db.query(Chat).filter(Chat.visitor_id == visitor_id).order_by(Chat.created_at).all()

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        # Step 1: search context in Qdrant
        context_docs = search_similar_vectors(request.message)

        # Step 2: get AI reply
        reply = generate_reply(request.message, context_docs)

        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))