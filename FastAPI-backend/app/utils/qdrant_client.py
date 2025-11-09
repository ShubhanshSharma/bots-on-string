from qdrant_client import QdrantClient
import os
from app.core.config import get_settings
from dotenv import load_dotenv

load_dotenv()
settings=get_settings()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY or None,
    prefer_grpc=False
)

def get_qdrant() -> QdrantClient:
    """
    Returns a configured Qdrant client.
    Uses environment variables for host and API key.
    """
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Qdrant: {str(e)}")
