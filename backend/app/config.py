import os
from dotenv import load_dotenv
from pathlib import Path

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'aics-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

    CHROMA_DB_HOST = os.getenv('CHROMA_DB_HOST', 'chromadb')
    CHROMA_DB_PORT = int(os.getenv('CHROMA_DB_PORT', 8000))

    # RAG 配置
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 512))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 50))
    TOP_K = int(os.getenv('TOP_K', 3))
