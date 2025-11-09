from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.visitor import Visitor
from app.models.chatbot import Chatbot
from app.schemas.visitor import VisitorCreate, VisitorOut
from app.core.database import get_db
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.visitor import Visitor
from app.models.visitor_session import VisitorSession

router = APIRouter(prefix="/visitor", tags=["visitor"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/session/start")
def start_visitor_session(chatbot_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Create a visitor and a new visitor session linked to a chatbot.
    """
    # 1️⃣ Create a new visitor
    visitor = Visitor(created_at=datetime.utcnow())
    db.add(visitor)
    db.commit()
    db.refresh(visitor)

    # 2️⃣ Create visitor session linked to chatbot
    session = VisitorSession(
        visitor_id=visitor.id,
        chatbot_id=chatbot_id,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 3️⃣ Return session info
    return {
        "message": "Visitor session started",
        "visitor_id": visitor.id,
        "session_id": session.id,
        "chatbot_id": chatbot_id,
    }

@router.post("/", response_model=VisitorOut)
def create_visitor(visitor: VisitorCreate, db: Session = Depends(get_db)):
    chatbot = db.query(Chatbot).filter(Chatbot.id == visitor.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    session_id = str(uuid.uuid4())
    new_visitor = Visitor(session_id=session_id, chatbot_id=visitor.chatbot_id)
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)
    return new_visitor

@router.get("/{session_id}", response_model=VisitorOut)
def get_visitor(session_id: str, db: Session = Depends(get_db)):
    visitor = db.query(Visitor).filter(Visitor.session_id == session_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # expire after 1 hour
    if datetime.utcnow() - visitor.created_at.replace(tzinfo=None) > timedelta(hours=1):
        db.delete(visitor)
        db.commit()
        raise HTTPException(status_code=410, detail="Session expired")

    return visitor

@router.get("/all")
def get_all_visitors(db: Session = Depends(get_db)):
    visitors = db.query(Visitor).all()
    return visitors