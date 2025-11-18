# app/services/chatbot_service.py
import os
import io
import math
import asyncio
from typing import List, Tuple, Optional
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
# from qdrant_client.http.models import PointStruct, VectorParams, Distance
from app.db.session import SessionLocal
from app.models.chatbot import Chatbot
from app.models.company import Company
from app.models.chat import Chat
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
import docx

# ---- CONFIG ----
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "smollm2:135m")  # generation model
QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_PREFIX = "chatbot_"  # final collection name: chatbot_{chatbot_id}

# initialize qdrant client
# qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant = QdrantClient("http://localhost:6333")

# ---- UTIL: file parsers ----
def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode(errors="ignore")

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    if lower.endswith(".txt") or lower.endswith(".md") or lower.endswith(".html"):
        return extract_text_from_txt(file_bytes)
    # fallback: try decode
    return extract_text_from_txt(file_bytes)

# ---- TEXT CHUNKER (simple) ----
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

# ---- OLLAMA EMBEDDING / GENERATE ----
async def ollama_embed(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Ollama — supports both /api/embed and /api/embeddings.
    Automatically detects which endpoint works.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {"model": EMBED_MODEL, "input": texts}

        # Try new endpoint first
        try:
            resp = await client.post(f"{OLLAMA_URL}/api/embeddings", json=payload)
            if resp.status_code == 404:
                # fallback to older endpoint
                resp = await client.post(f"{OLLAMA_URL}/api/embed", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Failed to get embeddings from Ollama: {str(e)}")

        # Normalize result (different models return slightly different structures)
        if "embedding" in data:
            return [data["embedding"]]
        elif "embeddings" in data:
            return data["embeddings"]
        elif "data" in data:
            return [d["embedding"] for d in data["data"]]
        else:
            raise ValueError(f"Unexpected Ollama embedding response: {data}")

async def ollama_generate(prompt: str, max_tokens: int = 512, stream: bool = False) -> str:
    """
    Call Ollama generate endpoint with the prompt, return text output.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "model": LLM_MODEL,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        url = f"{OLLAMA_URL}/api/generate"
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        body = resp.json()
        # Ollama output forms vary: check common keys:
        # Example: { "result": "..."} or {"text": "..."} or {"output": [{"generated_text": "..."}]}
        if isinstance(body, dict):
            if "text" in body:
                return body["text"]
            if "result" in body:
                # sometimes result is single text element
                r = body["result"]
                if isinstance(r, str):
                    return r
            if "output" in body and isinstance(body["output"], list):
                # try to find generated output
                first = body["output"][0]
                for k in ("generated_text", "text", "content"):
                    if k in first:
                        return first[k]
        # fallback: stringify
        return str(body)

# ---- QDRANT helpers ----
def ensure_collection(chatbot_id: int, vector_size: int = 768):
    collection_name = f"chatbot_{chatbot_id}"

    try:
        qdrant.get_collection(collection_name)
        return
    except Exception:
        print(f"⚙️ Creating new Qdrant collection: {collection_name}")

        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )




async def upsert_chunks_to_qdrant(chatbot_id: int, chunks: List[Tuple[str, dict]], vectors: List[List[float]]):
    """
    chunks: list of tuples (chunk_text, meta_dict)
    vectors: list of vectors aligned to chunks
    """
    collection_name = f"{COLLECTION_PREFIX}{chatbot_id}"
    vector_size = len(vectors[0]) if vectors else 0
    ensure_collection(chatbot_id, vector_size)

    points: List[PointStruct] = []
    for i, (chunk_text, meta) in enumerate(chunks):
        # create a stable id or leave None for qdrant to generate
        point_id = f"{chatbot_id}_{i}_{hash(chunk_text) & 0xFFFFFFFF}"
        points.append(PointStruct(id=point_id, vector=vectors[i], payload={"text": chunk_text, **meta}))
    qdrant.upsert(collection_name=collection_name, points=points)

# ---- HIGH LEVEL TRAIN (files) ----
async def train_chatbot_from_files(company_id: int, chatbot_id: int, files: List[Tuple[str, bytes]]):
    """
    files: list of tuples (filename, file_bytes)
    """
    # parse & chunk all files
    all_chunks: List[Tuple[str, dict]] = []
    for filename, file_bytes in files:
        text = extract_text_from_file(filename, file_bytes)
        if not text.strip():
            continue
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        for idx, c in enumerate(chunks):
            meta = {"source": filename, "chunk_index": idx}
            all_chunks.append((c, meta))

    if not all_chunks:
        return {"message": "No text extracted from files."}

    # call embeddings in batches (async)
    texts = [c for c, _ in all_chunks]
    BATCH = 16
    vectors = []
    for i in range(0, len(texts), BATCH):
        batch_texts = texts[i : i + BATCH]
        emb = await ollama_embed(batch_texts)
        vectors.extend(emb)

    # upsert to qdrant
    await upsert_chunks_to_qdrant(chatbot_id, all_chunks, vectors)
    return {"message": f"Indexed {len(all_chunks)} chunks into Qdrant for chatbot {chatbot_id}"}

# ---- TRAIN FROM URL (simple crawler) ----
import httpx
from bs4 import BeautifulSoup

async def train_chatbot_from_url(company_id: int, chatbot_id: int, url: str):
    # simple fetch + parse text
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        html = r.text
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts/styles
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    text = soup.get_text(separator="\n")
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    chunk_pairs = [(c, {"source": url, "chunk_index": i}) for i, c in enumerate(chunks)]

    # embed & upsert
    BATCH = 16
    vectors = []
    for i in range(0, len(chunks), BATCH):
        emb = await ollama_embed(chunks[i : i + BATCH])
        vectors.extend(emb)

    await upsert_chunks_to_qdrant(chatbot_id, chunk_pairs, vectors)
    return {"message": f"Crawled {len(chunks)} chunks from {url} and indexed into Qdrant."}

# ---- QUERY: RAG (search + generate) ----
def qdrant_search(chatbot_id: int, query_vector: List[float], top_k: int = 5):
    collection_name = f"{COLLECTION_PREFIX}{chatbot_id}"
    hits = qdrant.search(collection_name=collection_name, query_vector=query_vector, limit=top_k)
    return hits

async def query_chatbot(company_id: int, chatbot_id: int, question: str) -> dict:
    """
    Main query endpoint: embed question, retrieve from qdrant, call LLM with context.
    """
    # 1) embed question
    q_embs = await ollama_embed([question])
    q_vec = q_embs[0]

    # 2) search Qdrant
    try:
        hits = qdrant_search(chatbot_id, q_vec, top_k=5)
    except Exception as e:
        return {"error": f"Qdrant search error: {str(e)}"}

    # 3) build context
    context_pieces = []
    for h in hits:
        # payload contains 'text'
        payload = h.payload or {}
        text = payload.get("text") or ""
        src = payload.get("source")
        context_pieces.append(f"Source: {src}\n{text}")

    context = "\n\n---\n\n".join(context_pieces)
    prompt = (
        "You are a helpful assistant. Use the following context from the company's documents to answer the question.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nProvide a concise helpful answer and mention sources if present."
    )

    # 4) generate answer from Ollama
    answer = await ollama_generate(prompt, max_tokens=512)
    return {"answer": answer, "sources": [h.payload.get("source") for h in hits]}

# ---- convenience wrappers if your FastAPI endpoints call sync functions ----
def sync_train_files_wrapper(company_id: int, chatbot_id: int, files: List[Tuple[str, bytes]]):
    return asyncio.run(train_chatbot_from_files(company_id, chatbot_id, files))

def sync_train_url_wrapper(company_id: int, chatbot_id: int, url: str):
    return asyncio.run(train_chatbot_from_url(company_id, chatbot_id, url))

def sync_query_wrapper(company_id: int, chatbot_id: int, question: str):
    return asyncio.run(query_chatbot(company_id, chatbot_id, question))
