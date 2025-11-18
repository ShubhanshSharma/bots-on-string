import os
from sentence_transformers import SentenceTransformer

# Load the embedding model once (downloads automatically the first time)
# You can change this model name to others like "all-MiniLM-L12-v2" if you want higher accuracy.
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_with_sentence_transformer(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings locally using a sentence-transformers model.
    This version does NOT require Gemini API or any API key.
    """
    # Ensure input is a list of strings
    if isinstance(texts, str):
        texts = [texts]
    
    print(f"Generating embeddings for {len(texts)} text(s)...")

    # Generate embeddings (numpy array -> convert to list)
    embeddings = model.encode(texts).tolist()
    return embeddings


def embed_with_gemini(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings locally using a sentence-transformers model.
    This version does NOT require Gemini API or any API key.
    """
    # Ensure input is a list of strings
    if isinstance(texts, str):
        texts = [texts]
    
    print(f"Generating embeddings for {len(texts)} text(s)...")

    # Generate embeddings (numpy array -> convert to list)
    embeddings = model.encode(texts).tolist()
    return embeddings
