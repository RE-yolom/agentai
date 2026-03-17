import chromadb
from chromadb.config import Settings
import os

_chroma_client = None
_documents_collection = None
_sessions_collection = None

def init_chroma_client():
    """初始化 ChromaDB 客户端"""
    global _chroma_client, _documents_collection, _sessions_collection

    chroma_type = os.getenv("CHROMA_DB_TYPE", "persistent")

    if chroma_type == "http":
        host = os.getenv("CHROMA_DB_HOST", "localhost")
        port = int(os.getenv("CHROMA_DB_PORT", "8000"))
        try:
            _chroma_client = chromadb.HttpClient(host=host, port=port)
            print(f"Connected to remote ChromaDB at {host}:{port}")
        except Exception as e:
            print(f"Failed to connect to remote ChromaDB, falling back to persistent: {e}")
            _chroma_client = chromadb.PersistentClient(path='/app/chroma_db')
    else:
        # 使用持久化存储
        db_path = os.getenv("CHROMA_DB_PATH", "/app/chroma_db")
        _chroma_client = chromadb.PersistentClient(path=db_path)
        print(f"Using persistent ChromaDB at {db_path}")

    _documents_collection = _chroma_client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

    _sessions_collection = _chroma_client.get_or_create_collection(
        name="sessions"
    )

    return _chroma_client

def get_documents_collection():
    if _documents_collection is None:
        init_chroma_client()
    return _documents_collection

def get_sessions_collection():
    if _sessions_collection is None:
        init_chroma_client()
    return _sessions_collection
