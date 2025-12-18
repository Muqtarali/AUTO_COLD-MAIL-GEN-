# core/embeddings.py
from __future__ import annotations
import os
from chromadb.utils import embedding_functions
from core.config import SETTINGS

# Pre-download model to avoid long startup times
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".cache", "sentence_transformers"
)

_ef_cache = None

def get_embedding_function():
    """
    Returns a SentenceTransformers embedding function for Chroma.
    Caches the embedding function to avoid re-initialization.
    """
    global _ef_cache
    if _ef_cache is not None:
        return _ef_cache
    
    try:
        print(f"Creating embedding function with model: {SETTINGS.embed_model} and device: cpu")
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=SETTINGS.embed_model,
            device="cpu"
        )
        print("Embedding function created successfully")
        _ef_cache = ef
        return ef
    except Exception as e:
        print(f"Error creating embedding function: {e}")
        raise

__all__ = ["get_embedding_function"]
