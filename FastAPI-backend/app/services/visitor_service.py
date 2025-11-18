# # app/services/visitor_service.py
# import uuid
# import time
# from datetime import datetime, timedelta
# import asyncio

# from sqlalchemy.orm import Session
# from app.models.visitor import Visitor
# from app.models.chat import Chat
# from app.core.config import get_settings
# from app.utils.openai_client import generate_response
# from app.utils.qdrant_client import get_qdrant

# def create_visitor_session(db: Session, chatbot_id: int):
#     session_id = str(uuid.uuid4())
#     now = datetime.utcnow()
#     expires_at = now + timedelta(seconds=get_settings().SESSION_TTL_SECONDS)
#     vs = Visitor(session_id=session_id, chatbot_id=chatbot_id, created_at=now, expires_at=expires_at)
#     db.add(vs)
#     db.commit()
#     db.refresh(vs)
#     return vs

# def get_session_by_id(db: Session, session_id: str):
#     return db.query(Visitor).filter(Visitor.session_id == session_id).first()

# def append_message(db: Session, visitor: Visitor, role: str, content: str):
#     cm = Chat(visitor_id=visitor.id, role=role, content=content)
#     db.add(cm)
#     db.commit()
#     db.refresh(cm)
#     return cm

# async def handle_user_message(db: Session, visitor: Visitor, user_text: str):
#     # Build chat history as a list of messages for OpenAI.
#     msgs = []
#     chats = db.query(Chat).filter(Chat.visitor_id == visitor.id).order_by(Chat.created_at).all()
#     for c in chats:
#         msgs.append({"role": c.role, "content": c.content})

#     # add user
#     append_message(db, visitor, "user", user_text)

#     # call OpenAI (async wrapper)
#     bot_text = await generate_response(user_text, history=msgs)

#     append_message(db, visitor, "bot", bot_text)
#     return bot_text

# # Background cleanup: deletes sessions and Chats older than expiry.
# async def cleanup_expired_sessions_task(interval_seconds: int = 300):
#     """
#     Runs forever until cancelled; every `interval_seconds` it deletes expired sessions.
#     """
#     import asyncio
#     from app.core.database import SessionLocal
#     while True:
#         try:
#             db = SessionLocal()
#             now = datetime.utcnow()
#             expired = db.query(Visitor).filter(Visitor.expires_at <= now).all()
#             expired_ids = [s.id for s in expired]
#             if expired_ids:
#                 db.query(Chat).filter(Chat.visitor_id.in_(expired_ids)).delete(synchronize_session=False)
#                 db.query(Visitor).filter(Visitor.id.in_(expired_ids)).delete(synchronize_session=False)
#                 db.commit()
#             db.close()
#         except asyncio.CancelledError:
#             raise
#         except Exception as e:
#             print("Error during cleanup:", e)
#         await asyncio.sleep(interval_seconds)
