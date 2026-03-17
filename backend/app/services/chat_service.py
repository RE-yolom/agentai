import uuid
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.rag_service import get_documents_collection
from app.config import Config

# 阿里云 DashScope 配置
API_KEY = Config.DASHSCOPE_API_KEY

class RAGService:
    def __init__(self):
        self.collection = get_documents_collection()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len
        )

    def add_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """添加文档到向量数据库"""
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分割文档
        chunks = self.text_splitter.split_text(content)

        # 生成文档 ID
        doc_id = str(uuid.uuid4())

        # 添加到 ChromaDB
        if chunks:
            self.collection.add(
                documents=chunks,
                metadatas=[{"doc_id": doc_id, "filename": filename} for _ in chunks],
                ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
            )

        return {"id": doc_id, "filename": filename, "chunks": len(chunks)}

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """检索相关文档"""
        if top_k is None:
            top_k = Config.TOP_K

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        if not results['documents'] or not results['documents'][0]:
            return []

        sources = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            # 将距离转换为相似度分数
            distance = results['distances'][0][i] if results['distances'] else 0
            score = 1 / (1 + distance)

            sources.append({
                "content": doc,
                "doc_id": metadata.get("doc_id", ""),
                "score": score
            })

        return sources

    def delete_document(self, doc_id: str):
        """删除文档"""
        # 查找所有属于该文档的 chunk
        results = self.collection.get(
            where={"doc_id": doc_id},
            include=[]
        )

        if results and results['ids']:
            self.collection.delete(ids=results['ids'])

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档元数据"""
        results = self.collection.get(include=["metadatas"])

        if not results or not results['metadatas']:
            return []

        # 去重
        doc_map = {}
        for metadata in results['metadatas']:
            doc_id = metadata.get('doc_id', '')
            if doc_id and doc_id not in doc_map:
                doc_map[doc_id] = {
                    "id": doc_id,
                    "filename": metadata.get('filename', '未知文件'),
                    "status": 'completed'
                }

        return list(doc_map.values())


def generate_reply(query: str, context: str, history: List[Dict] = None) -> str:
    """使用阿里云 DashScope API 生成回复"""
    import dashscope
    from dashscope import Generation

    # 设置 API Key
    dashscope.api_key = API_KEY

    system_prompt = """你是一个智能客服助手。请根据提供的上下文信息回答用户的问题。
如果上下文中有相关信息，请基于上下文回答。
如果上下文中没有相关信息，请根据你的知识回答。
回答要简洁、准确、友好。"""

    # 构建用户输入
    if context:
        prompt = f"参考上下文：\n{context}\n\n用户问题：{query}"
    else:
        prompt = query

    # 构建消息历史
    messages = []
    if history:
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            messages.append({'role': role, 'content': content})

    # 添加当前查询
    messages.append({'role': 'user', 'content': prompt})

    try:
        # 使用 DashScope Generation API 调用
        response = Generation.call(
            model='qwen-turbo',
            messages=messages
        )

        # 解析响应
        if response.status_code == 200:
            return response.output.text
        else:
            return f"抱歉，AI 服务响应失败：{response.code} - {response.message}"
    except Exception as e:
        return f"抱歉，发生错误：{str(e)}"
