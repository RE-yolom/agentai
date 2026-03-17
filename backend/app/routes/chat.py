import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.chat_service import RAGService, generate_reply

chat_bp = Blueprint('chat', __name__)

_sessions_db = {}

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id')

    if not message:
        return jsonify({"success": False, "error": "消息不能为空"}), 400

    # 初始化 RAG 服务
    rag_service = RAGService()

    # 检索相关文档
    sources = rag_service.search(message)

    # 构建上下文
    context = ""
    if sources:
        context = "\n\n".join([s["content"] for s in sources])

    # 获取会话历史
    history = []
    if session_id and session_id in _sessions_db:
        history = _sessions_db[session_id].get('messages', [])

    # 生成回复
    reply = generate_reply(message, context, history)

    # 保存消息到会话
    if session_id:
        if session_id not in _sessions_db:
            _sessions_db[session_id] = {
                'id': session_id,
                'name': '新会话',
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

        _sessions_db[session_id]['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        _sessions_db[session_id]['messages'].append({
            'role': 'assistant',
            'content': reply,
            'timestamp': datetime.now().isoformat()
        })
        _sessions_db[session_id]['updated_at'] = datetime.now().isoformat()

        # 更新会话名称
        if _sessions_db[session_id]['name'] == '新会话':
            _sessions_db[session_id]['name'] = message[:20] + '...' if len(message) > 20 else message

    # 构建响应
    response_data = {
        "success": True,
        "data": {
            "reply": reply,
            "sources": sources
        }
    }

    return jsonify(response_data)
