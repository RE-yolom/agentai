import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify

session_bp = Blueprint('session', __name__)

# 内存存储会话
_sessions_db = {}

@session_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """获取所有会话"""
    sessions = list(_sessions_db.values())
    # 按更新时间排序
    sessions.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

    # 返回简化格式
    result = [{
        'id': s['id'],
        'name': s['name'],
        'created_at': s['created_at'],
        'updated_at': s['updated_at']
    } for s in sessions]

    return jsonify({"success": True, "data": result})

@session_bp.route('/sessions', methods=['POST'])
def create_session():
    """创建新会话"""
    data = request.get_json() or {}
    name = data.get('name', '新会话')

    session_id = str(uuid.uuid4())
    session = {
        'id': session_id,
        'name': name,
        'messages': [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    _sessions_db[session_id] = session

    return jsonify({
        "success": True,
        "data": {
            'id': session_id,
            'name': name,
            'created_at': session['created_at'],
            'updated_at': session['updated_at']
        }
    })

@session_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话详情"""
    if session_id not in _sessions_db:
        return jsonify({"success": False, "error": "会话不存在"}), 404

    session = _sessions_db[session_id]
    return jsonify({
        "success": True,
        "data": session
    })

@session_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    if session_id not in _sessions_db:
        return jsonify({"success": False, "error": "会话不存在"}), 404

    del _sessions_db[session_id]
    return jsonify({"success": True})
