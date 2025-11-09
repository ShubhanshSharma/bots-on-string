# app/api/api_v1/routes/chatbot.py
from typing import List, Generator, Optional

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chatbot import ChatbotCreate, ChatbotRead, ChatbotUpdate, ChatbotOut
from app.models.chatbot import Chatbot
from app.models.company import Company

# service functions that integrate LangChain + Qdrant; implemented in app.services.chatbot_service
from app.services.chatbot_service import (
    train_chatbot_from_files,
    train_chatbot_from_url,
    query_chatbot,
)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def get_db() -> Generator[Session, None, None]:
    """
    Simple DB dependency using your SessionLocal factory.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#
# CRUD for Chatbots
#
@router.post("/create", response_model=ChatbotRead, status_code=status.HTTP_201_CREATED)
def create_chatbot(payload: ChatbotCreate, db: Session = Depends(get_db)):
    company = db.get(Company, payload.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    bot = Chatbot(name=payload.name, description=payload.description, company_id=payload.company_id)
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot


@router.get("/", response_model=List[ChatbotOut])
def list_chatbots(db: Session = Depends(get_db)):
    return db.query(Chatbot).all()


@router.get("/company/{company_id}", response_model=List[ChatbotOut])
def list_company_chatbots(company_id: int, db: Session = Depends(get_db)):
    return db.query(Chatbot).filter(Chatbot.company_id == company_id).all()


@router.get("/{chatbot_id}", response_model=ChatbotOut)
def read_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    bot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    return bot


@router.put("/{chatbot_id}", response_model=ChatbotOut)
def update_chatbot(chatbot_id: int, data: ChatbotUpdate, db: Session = Depends(get_db)):
    bot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")

    if data.name is not None:
        bot.name = data.name
    if data.description is not None:
        bot.description = data.description

    db.commit()
    db.refresh(bot)
    return bot


@router.delete("/{chatbot_id}", status_code=status.HTTP_200_OK)
def delete_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    bot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    db.delete(bot)
    db.commit()
    return {"message": "Chatbot deleted successfully"}


#
# Training endpoints
#
@router.post("/train-files", status_code=status.HTTP_202_ACCEPTED)
async def train_chatbot_files(
    company_id: int = Form(...),
    chatbot_id: int = Form(...),
    files: List[UploadFile] = File(...),
):
    """
    Accept multiple files (pdf/docx/txt/html) and send them to the training pipeline.
    The training pipeline should parse files -> split -> embed -> store vectors in Qdrant.
    """
    # Optional: basic validation
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

    try:
        # The service should accept UploadFile list and handle parsing/embedding/storage
        result = await train_chatbot_from_files(company_id=company_id, chatbot_id=chatbot_id, files=files)
        # result can be a dict with status/message/details
        return {"status": "ok", "detail": result}
    except Exception as exc:
        # Bubble up useful error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/train-url", status_code=status.HTTP_202_ACCEPTED)
async def train_chatbot_url(
    company_id: int = Form(...),
    chatbot_id: int = Form(...),
    url: str = Form(...),
):
    """
    Crawl a website (or single page) and train the chatbot from the crawled text.
    Service should handle politeness, robots.txt, text extraction, splitting, embedding, Qdrant upsert.
    """
    if not url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL is required")
    try:
        result = await train_chatbot_from_url(company_id=company_id, chatbot_id=chatbot_id, url=url)
        return {"status": "ok", "detail": result}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


#
# Query endpoint — this is the endpoint your frontend expects:
# POST /chatbot/{chatbot_id}/query  with JSON body: { "company_id": 1, "query": "hello" }
#
@router.post("/{chatbot_id}/query")
async def query_chatbot_route(chatbot_id: int, payload: dict):
    """
    Query the trained chatbot. Payload must include company_id and query text.
    The service should: find the correct Qdrant collection (or namespace) for company/chatbot,
    run embedding for the query, retrieve top-k, run LangChain re-ranker / LLM to compose answer,
    and return a response dict like {"answer": "...", "source_documents": [...]}.
    """
    company_id = payload.get("company_id")
    question = payload.get("query") or payload.get("question") or payload.get("q")

    if not company_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_id is required in payload")
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="query is required in payload")

    try:
        response = await query_chatbot(company_id=company_id, chatbot_id=chatbot_id, question=question)
        # Expecting response to be a dict or string. Standardize:
        if isinstance(response, dict):
            return response
        return {"answer": str(response)}
    except ValueError as ve:
        # service can raise ValueError if chatbot / collection not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
