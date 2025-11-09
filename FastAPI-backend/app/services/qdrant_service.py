from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from app.core.config import get_settings
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

settings = get_settings()

# Initialize Qdrant client
# qdrant = QdrantClient(url=settings.QDRANT_URL)
qdrant = QdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")
COLLECTION_NAME = "company_documents"

def init_collection():
    """
    Initialize Qdrant collection if it doesn't exist.
    """
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

def store_vector(company_id: str, vector: list[float], text: str):
    """
    Store vector and text data into Qdrant.
    """
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=None,
                vector=vector,
                payload={"company_id": company_id, "text": text},
            )
        ],
    )

def search_similar(company_id: str, query_vector: list[float], limit: int = 3):
    """
    Search for similar vectors belonging to the same company.
    """
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter={
            "must": [
                {"key": "company_id", "match": {"value": company_id}},
            ]
        },
        limit=limit,
    )
    return [r.payload["text"] for r in results]

def search_similar_vectors(query: str):
    vector = model.encode(query).tolist()
    hits = qdrant.search(
        collection_name="chatbot_docs",
        query_vector=vector,
        limit=3
    )
    return [hit.payload.get("text") for hit in hits]

# app/services/qdrant_service.py
from qdrant_client import QdrantClient

def get_qdrant_client():
    # read host/port from settings in app.core.config
    from app.core.config import settings
    return QdrantClient(url=settings.QDRANT_URL)
