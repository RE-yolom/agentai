import logging
from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import chat_bp, document_bp, session_bp
from .services.rag_service import init_chroma_client

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 初始化 ChromaDB 客户端
    init_chroma_client(app.config['CHROMA_DB_HOST'], app.config['CHROMA_DB_PORT'])

    # 注册蓝图
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(document_bp, url_prefix='/api')
    app.register_blueprint(session_bp, url_prefix='/api')

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    return app
