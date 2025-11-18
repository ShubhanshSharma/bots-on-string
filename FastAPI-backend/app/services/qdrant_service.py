# app/services/qdrant_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings

settings = get_settings()
QDRANT_URL = settings.QDRANT_URL  # e.g. "http://localhost:6333"

# single client used everywhere
qdrant = QdrantClient(url=QDRANT_URL)

# model you'll use for embeddings (you already used all-MiniLM-L6-v2)
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_SIZE = EMBED_MODEL.get_sentence_embedding_dimension()

# collection name (you may change per company/chatbot later)
COLLECTION_NAME = "company_documents"

def init_qdrant_collection(collection_name: str = COLLECTION_NAME):
    """Create collection with correct vector size if it doesn't exist."""
    existing = [c.name for c in qdrant.get_collections().collections]
    if collection_name in existing:
        return False  # existed already
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    return True


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





# shubhansh code:
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.services.qdrant_service import qdrant, EMBED_MODEL, COLLECTION_NAME

def retrieve_chunks(query: str, chatbot_id: int, top_k: int = 3):
    """Search Qdrant for relevant context chunks."""
    query_vec = EMBED_MODEL.encode([query])[0].tolist()

    # Filter: only return chunks belonging to this chatbot
    query_filter = Filter(
        must=[
            FieldCondition(
                key="chatId",
                match=MatchValue(value=str(chatbot_id))
            )
        ]
    )

    # Perform similarity search
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
        query_filter=query_filter
    )

    # Extract chunk texts
    chunks = [result.payload["text"] for result in results]

    return chunks
