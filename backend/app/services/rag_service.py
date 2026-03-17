import chromadb
from chromadb.config import Settings

_chroma_client = None
_documents_collection = None
_sessions_collection = None

def init_chroma_client(host: str, port: int):
    """初始化 ChromaDB 客户端"""
    global _chroma_client, _documents_collection, _sessions_collection

    try:
        _chroma_client = chromadb.HttpClient(host=host, port=port)
        print(f"Connected to ChromaDB at {host}:{port}")
    except Exception as e:
        print(f"Failed to connect to remote ChromaDB, using persistent client: {e}")
        _chroma_client = chromadb.PersistentClient(path='/chroma_db')

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
        init_chroma_client('localhost', 8000)
    return _documents_collection

def get_sessions_collection():
    if _sessions_collection is None:
        init_chroma_client('localhost', 8000)
    return _sessions_collection
