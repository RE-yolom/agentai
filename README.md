# AI 智能客服系统

基于 Vue3 + Flask + RAG 技术的智能客服系统，支持知识库管理和智能问答，可通过 Docker 一键部署到阿里云服务器。

## 技术架构

- **前端**: Vue 3 + TypeScript + Vite + Element Plus
- **后端**: Python Flask
- **RAG 框架**: LangChain
- **向量数据库**: ChromaDB
- **大模型**: 阿里云百炼 (通义千问)
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx

## 功能特性

- 💬 实时智能对话
- 📚 知识库文档管理 (支持 txt/md/pdf/doc 格式)
- 🔍 RAG 检索增强生成
- 📱 响应式 UI 界面
- 🐳 Docker 一键部署
- 🔐 CORS 跨域支持

## 快速开始

### 1. 获取 API Key

访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/apiKey) 获取 API Key。

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key:

```bash
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3. 本地开发运行

#### 方式一：分别启动前后端

**启动后端:**
```bash
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端将在 `http://localhost:5000` 启动。

**启动前端:**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动。

#### 方式二：Docker Compose 一键启动

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 访问 http://localhost
```

### 4. 部署到阿里云 Linux 服务器

#### 步骤 1: 准备服务器

- 阿里云 ECS 实例 (推荐 2 核 4G 以上)
- 开放安全组端口：80 (HTTP)

#### 步骤 2: 上传项目

```bash
# 方式一：使用 scp 上传
scp -r . root@your-server-ip:/opt/aics/

# 方式二：使用 Git 克隆
git clone <your-repo> /opt/aics/
cd /opt/aics/
```

#### 步骤 3: 执行部署脚本

```bash
cd /opt/aics

# 赋予执行权限
chmod +x deploy.sh

# 执行部署 (自动安装 Docker 并启动服务)
sudo ./deploy.sh
```

**或者使用 start.sh 脚本（需要预先安装 Docker）：**

```bash
chmod +x start.sh
./start.sh
```

#### 步骤 4: 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试访问
curl http://localhost
```

现在可以通过 `http://your-server-ip` 访问系统。

**详细说明请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)**

## 目录结构

```
.
├── docker-compose.yml      # Docker 编排配置
├── Dockerfile.frontend     # 前端 Docker 配置（已修复 nginx 配置问题）
├── Dockerfile.backend      # 后端 Docker 配置
├── nginx.conf              # Nginx 反向代理配置（主服务）
├── start.sh                # 快速启动脚本（本地开发）
├── deploy.sh               # 一键部署脚本（服务器）
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── DEPLOYMENT.md           # 详细部署文档
├── PDR.md                  # 项目设计文档
├── README.md               # 使用说明
├── frontend/               # Vue3 前端项目
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── types/         # TypeScript 类型
│   │   ├── router/        # 路由配置
│   │   ├── utils/         # 工具函数
│   │   ├── App.vue        # 根组件
│   │   └── main.ts        # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── backend/                # Flask 后端项目
    ├── app/
    │   ├── routes/        # API 路由 (chat.py, document.py, session.py)
    │   ├── services/      # 业务逻辑 (chat_service.py, rag_service.py)
    │   ├── config.py      # 配置文件
    │   └── __init__.py    # 应用初始化
    ├── main.py            # 应用入口
    └── requirements.txt   # Python 依赖
```

## API 接口说明

### Chat API

**发送消息**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "你好，我想咨询产品价格",
  "session_id": "uuid-string"
}

Response:
{
  "success": true,
  "data": {
    "reply": "您好！我们的产品价格如下...",
    "sources": [
      {
        "doc_id": "xxx",
        "content": "...",
        "score": 0.95
      }
    ]
  }
}
```

### Document API

**上传文档**
```http
POST /api/documents
Content-Type: multipart/form-data

file: [文件]
```

**获取文档列表**
```http
GET /api/documents
```

**删除文档**
```http
DELETE /api/documents/:id
```

### Session API

**获取会话列表**
```http
GET /api/sessions
```

**创建会话**
```http
POST /api/sessions
Content-Type: application/json

{
  "name": "新会话"
}
```

**删除会话**
```http
DELETE /api/sessions/:id
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key (必填，使用通义千问模型) | - |
| `FLASK_ENV` | Flask 运行环境 | `production` |
| `FLASK_SECRET_KEY` | Flask 密钥 | `aics-secret-key` |
| `BACKEND_PORT` | 后端服务端口 | `5000` |
| `CHROMA_DB_HOST` | ChromaDB 主机地址 | `chromadb` (Docker 模式) |
| `CHROMA_DB_PORT` | ChromaDB 端口 | `8000` |
| `CHROMA_DB_TYPE` | ChromaDB 类型 | `persistent` (持久化) |
| `CHROMA_DB_PATH` | ChromaDB 数据路径 | `/app/chroma_db` |
| `CHUNK_SIZE` | 文档分块大小 | `512` |
| `CHUNK_OVERLAP` | 分块重叠大小 | `50` |
| `TOP_K` | 检索返回数量 | `3` |
| `MAX_CONTENT_LENGTH` | 最大上传文件大小 (字节) | `52428800` |

## 常用命令

### Docker 相关

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose up -d --build

# 清理数据卷
docker-compose down -v
```

### 前端命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 故障排查

### 1. 后端启动失败

```bash
# 检查 Python 版本 (需要 3.9+)
python --version

# 检查依赖安装
pip install -r requirements.txt

# 查看后端日志
docker-compose logs backend
```

### 2. 前端无法连接后端

检查 `vite.config.ts` 中的代理配置：

```javascript
proxy: {
  '/api': {
    target: 'http://backend:5000',
    changeOrigin: true
  }
}
```

### 3. ChromaDB 相关问题

后端使用持久化 ChromaDB，数据存储在 Docker 数据卷中：

```bash
# 查看 ChromaDB 数据卷
docker volume ls | grep chroma_data

# 备份数据
docker run --rm \
    -v ai_chroma_data:/source \
    -v $(pwd):/backup \
    alpine tar czf chroma_backup.tar.gz -C /source .
```

### 4. API Key 无效

确保 `.env` 文件中的 `DASHSCOPE_API_KEY` 配置正确，并且已重新加载环境变量：

```bash
# Docker 部署需要重启服务
docker-compose restart backend
```

## 性能优化建议

1. **增加 CHUNK_SIZE**: 如果文档较长，可增加分块大小到 2048
2. **调整 TOP_K**: 根据实际需求调整检索返回数量
3. **使用 SSD 存储**: ChromaDB 使用持久化存储时，SSD 性能更好
4. **增加服务器内存**: 推荐 4GB 以上内存

## 安全建议

1. **修改默认密钥**: 务必修改 `FLASK_SECRET_KEY`
2. **配置防火墙**: 仅开放必要端口
3. **使用 HTTPS**: 生产环境建议配置 SSL 证书
4. **定期备份**: 定期备份 ChromaDB 数据卷

## 扩展功能

### 添加新的文档类型支持

编辑 `backend/app/routes/document.py`:

```python
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'doc', 'docx', 'xlsx'}
```

### 更换大模型

编辑 `backend/app/services/chat_service.py`:

```python
response = Generation.call(
    model='qwen-max',  # 修改模型
    messages=messages
)
```

### 自定义系统提示词

编辑 `backend/app/services/chat_service.py`:

```python
system_prompt = """你是一个专业的客服助手..."""
```

## 技术支持

如有问题，请查看:

- [PDR.md](./PDR.md) - 项目设计文档
- [LangChain 文档](https://python.langchain.com/)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [阿里云百炼文档](https://help.aliyun.com/zh/dashscope/)

## License

MIT License
