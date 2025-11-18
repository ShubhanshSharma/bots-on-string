# app/api/upload_routes.py
from fastapi import APIRouter, HTTPException
from qdrant_client.models import PointStruct
from app.services.qdrant_service import qdrant, EMBED_MODEL, COLLECTION_NAME
import uuid
from app.models.chatbot import Chatbot

router = APIRouter(prefix="/upload", tags=["upload"])
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pdfminer.high_level import extract_text
from qdrant_client.http.models import PointStruct
import uuid, os
from app.db.session import SessionLocal
from sqlalchemy.orm import Session


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def extract_pdf_text(file_path: str) -> str:
    try:
        return extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {e}")


@router.post("/upload")
async def upload_pdf(
    companyId: str = Form(...),   # <-- accept string
    chatName: str = Form(...),    # <-- accept string
    file: UploadFile = File(...),
):
    db: Session = get_db()

    # Convert ID to integer safely
    try:
        company_id_int = int(companyId)
    except:
        raise HTTPException(status_code=400, detail="companyId must be an integer")

    # 1️⃣ Validate company exists
    from app.models.company import Company
    company = db.query(Company).filter(Company.id == company_id_int).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 2️⃣ Create Chatbot in Postgres
    new_chatbot = Chatbot(
        name=chatName,
        description="Uploaded PDF",
        company_id=company_id_int,
    )
    db.add(new_chatbot)
    db.commit()
    db.refresh(new_chatbot)

    chatbot_id = new_chatbot.id

    # --- PDF FILE VALIDATION ---
    filename = file.filename.lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    text = extract_pdf_text(temp_path)

    if not text.strip():
        raise HTTPException(status_code=400, detail="PDF contains no text")

    # --- Chunking ---
    CHUNK_SIZE = 500
    OVERLAP = 100
    step = CHUNK_SIZE - OVERLAP

    chunks = [
        text[i: i + CHUNK_SIZE]
        for i in range(0, len(text), step)
        if text[i: i + CHUNK_SIZE].strip()
    ]

    embeddings = EMBED_MODEL.encode(chunks, show_progress_bar=False)

    # --- Store in Qdrant ---
    points = []
    for i, emb in enumerate(embeddings):
        vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload={
                    "companyId": company_id_int,
                    "chatbotId": chatbot_id,
                    "chatName": chatName,
                    "chunk_index": i,
                    "text": chunks[i],
                },
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

    # Remove temp file
    try:
        os.remove(temp_path)
    except:
        pass

    return {
        "status": "success",
        "chatbot_id": chatbot_id,
        "chunks_stored": len(points),
    }
