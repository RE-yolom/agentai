import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.chat_service import RAGService

document_bp = Blueprint('document', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/documents', methods=['GET'])
def get_documents():
    """获取文档列表"""
    rag_service = RAGService()
    documents = rag_service.get_all_documents()
    return jsonify({"success": True, "data": documents})

@document_bp.route('/documents', methods=['POST'])
def upload_document():
    """上传文档"""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "未找到文件"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "文件名为空"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "不支持的文件类型"}), 400

    # 创建上传目录
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # 保存文件
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    file.save(file_path)

    try:
        # 添加到 RAG
        rag_service = RAGService()
        result = rag_service.add_document(file_path, filename)

        # 删除临时文件
        os.remove(file_path)

        return jsonify({
            "success": True,
            "data": {
                "id": result["id"],
                "filename": filename,
                "status": "completed"
            }
        })
    except Exception as e:
        # 清理失败的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"success": False, "error": str(e)}), 500

@document_bp.route('/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除文档"""
    try:
        rag_service = RAGService()
        rag_service.delete_document(doc_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
