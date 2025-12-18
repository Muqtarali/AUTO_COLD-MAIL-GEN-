# core/stores.py
from __future__ import annotations
import os
import json
from typing import Any, Dict
import chromadb
from core.embeddings import get_embedding_function
from chromadb.utils import embedding_functions
from chromadb.config import Settings

# Fixed absolute path so both scripts use the same DB
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VECTOR_DIR = os.path.abspath(os.path.join(BASE_DIR, "vectorstore"))

_resume_client = None
_jd_client = None
_resume_store = None
_jd_store = None

def _coerce_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all metadata values are Chroma-compatible."""
    safe_meta = {}
    for k, v in (meta or {}).items():
        if isinstance(v, (list, dict, set, tuple)):
            safe_meta[k] = json.dumps(v, ensure_ascii=False)
        elif isinstance(v, (str, int, float, bool)) or v is None:
            safe_meta[k] = v
        else:
            safe_meta[k] = str(v)
    return safe_meta

def get_resume_store():
    global _resume_client, _resume_store

    if _resume_store is not None:
        return _resume_store

    db_path = os.environ.get("RESUME_DB_PATH", os.path.join(VECTOR_DIR, "resumes"))
    _resume_client = _resume_client or chromadb.PersistentClient(
        path=db_path,
        settings=Settings(
            anonymized_telemetry=False
        ),
    )
    sentence_transformer_ef = get_embedding_function()
    _resume_store = _resume_client.get_or_create_collection(
        name="resumes",
        embedding_function=sentence_transformer_ef,
    )
    return _resume_store

def get_jd_store():
    global _jd_client, _jd_store

    if _jd_store is not None:
        return _jd_store

    db_path = os.environ.get("JD_DB_PATH", os.path.join(VECTOR_DIR, "jds"))
    _jd_client = _jd_client or chromadb.PersistentClient(
        path=db_path,
        settings=Settings(
            anonymized_telemetry=False
        ),
    )
    sentence_transformer_ef = get_embedding_function()
    _jd_store = _jd_client.get_or_create_collection(
        name="jds",
        embedding_function=sentence_transformer_ef,
    )
    return _jd_store

def upsert_doc(col, _id: str, document: str, metadata: Dict[str, Any]):
    print(f"upsert_doc called with _id={_id}")
    safe_meta = _coerce_metadata(metadata or {})
    # Chroma 0.6+ requires metadata dict to have at least one attribute.
    if not isinstance(safe_meta, dict) or len(safe_meta) == 0:
        safe_meta = {"doc_type": "unknown"}
    print(f"Metadata after coercion: {safe_meta}")
    try:
        col.upsert(ids=[_id], documents=[document], metadatas=[safe_meta])
        print("upsert_doc completed successfully")
    except Exception as e:
        print(f"Exception in upsert_doc: {e}")
        raise

def query(col, text: str, top_k: int = 5):
    return col.query(query_texts=[text], n_results=top_k)
