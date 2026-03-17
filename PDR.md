# AI 智能客服系统 - 项目设计文档 (PDR)

## 1. 项目概述

### 1.1 项目名称
AI Intelligent Customer Service (AICS) - AI 智能客服系统

### 1.2 项目目标
构建一个基于 RAG(检索增强生成) 技术的 AI 智能客服系统，支持知识库管理、智能问答、多轮对话等功能，可通过 Docker 部署到阿里云服务器。

### 1.3 技术栈
| 组件 | 技术选型 |
|------|----------|
| 前端框架 | Vue 3 + TypeScript |
| 构建工具 | Vite 5.x |
| UI 组件库 | Element Plus |
| 后端框架 | Python Flask |
| RAG 框架 | LangChain |
| 向量数据库 | ChromaDB |
| 大模型 API | 阿里云百炼 (通义千问) |
| 容器化 | Docker + Docker Compose |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (反向代理)                          │
│                    Port: 80/443                              │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Vue3 Frontend        │     │    Flask Backend        │
│    Port: 5173           │     │    Port: 5000           │
│    (静态文件)            │     │    (API 服务)            │
└─────────────────────────┘     └─────────────────────────┘
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                    ┌─────────────────┐   ┌─────────────────┐
                    │   ChromaDB      │   │  阿里云百炼 API  │
                    │   (向量数据库)   │   │   (LLM 服务)     │
                    └─────────────────┘   └─────────────────┘
```

### 2.2 目录结构

```
aics/
├── docker-compose.yml          # Docker 编排配置
├── Dockerfile.frontend         # 前端 Docker 配置
├── Dockerfile.backend          # 后端 Docker 配置
├── nginx.conf                  # Nginx 配置
├── .env                        # 环境变量配置
├── README.md                   # 项目说明
├── PDR.md                      # 项目设计文档
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── types/             # TypeScript 类型
│   │   ├── utils/             # 工具函数
│   │   ├── App.vue            # 根组件
│   │   └── main.ts            # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── backend/                    # 后端项目
    ├── app/
    │   ├── __init__.py        # Flask 应用初始化
    │   ├── routes/            # 路由模块
    │   ├── services/          # 业务逻辑
    │   ├── models/            # 数据模型
    │   ├── utils/             # 工具函数
    │   └── config.py          # 配置文件
    ├── requirements.txt       # Python 依赖
    └── main.py               # 应用入口
```

---

## 3. 功能模块设计

### 3.1 前端功能模块

| 模块 | 功能描述 |
|------|----------|
| 聊天界面 | 实时对话、消息展示、输入框、发送按钮 |
| 知识库管理 | 文档上传、解析、删除、列表展示 |
| 对话历史 | 历史会话列表、会话切换、删除会话 |
| 设置面板 | API 配置、系统设置 |

### 3.2 后端功能模块

| 模块 | 功能描述 |
|------|----------|
| Chat API | 处理聊天请求、调用 RAG 检索、返回 AI 回复 |
| Document API | 文档上传、解析、向量存储、删除 |
| Session API | 会话管理、历史记录存储 |
| RAG Service | 文档分块、向量化、相似度检索 |

---

## 4. API 接口设计

### 4.1 RESTful API

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/chat` | POST | 发送消息并获取 AI 回复 |
| `/api/documents` | GET | 获取文档列表 |
| `/api/documents` | POST | 上传文档 |
| `/api/documents/:id` | DELETE | 删除文档 |
| `/api/sessions` | GET | 获取会话列表 |
| `/api/sessions/:id` | GET | 获取会话详情 |
| `/api/sessions/:id` | DELETE | 删除会话 |

### 4.2 请求/响应示例

#### Chat API
```json
// POST /api/chat
// Request
{
  "message": "你好，我想咨询一下产品价格",
  "session_id": "uuid-string"
}

// Response
{
  "success": true,
  "data": {
    "reply": "您好！我们的产品价格如下...",
    "sources": [
      {"doc_id": "1", "content": "...", "score": 0.95}
    ]
  }
}
```

---

## 5. 数据模型设计

### 5.1 ChromaDB Collection

```
Collection: documents
- id: string (文档唯一标识)
- content: string (文档内容/分块)
- metadata: {
    filename: string,
    upload_time: string,
    file_type: string
  }
- embedding: float[] (向量表示)

Collection: sessions
- id: string (会话 ID)
- messages: json (对话历史)
- created_at: string
```

---

## 6. Docker 部署方案

### 6.1 服务配置

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| frontend | node:20-alpine | 5173 | Vue 前端 |
| backend | python:3.11-slim | 5000 | Flask 后端 |
| chromadb | chromadb/chroma | 8000 | 向量数据库 |
| nginx | nginx:alpine | 80 | 反向代理 |

### 6.2 部署流程

1. 构建 Docker 镜像
2. 启动 Docker Compose 服务
3. 配置 Nginx 反向代理
4. 配置防火墙和安全组
5. 验证服务运行状态

---

## 7. 环境变量配置

```bash
# 阿里云百炼 API 配置
DASHSCOPE_API_KEY=your-api-key

# 后端配置
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key
BACKEND_PORT=5000

# ChromaDB 配置
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000

# 前端配置
VITE_API_BASE_URL=/api
```

---

## 8. 安全考虑

- API Key 通过环境变量管理，不硬编码
- CORS 跨域配置限制
- 请求频率限制
- 文件上传类型和大小限制
- 敏感信息加密存储

---

## 9. 性能优化

- 向量检索使用 ChromaDB 索引
- 文档分块大小优化 (512-1024 tokens)
- 响应流式输出 (SSE)
- 前端静态资源 CDN 加速
- Nginx 缓存配置

---

## 10. 实施计划

### 阶段一：基础架构搭建
- [ ] 创建项目目录结构
- [ ] 配置 Docker Compose
- [ ] 配置 Nginx

### 阶段二：后端开发
- [ ] Flask 应用初始化
- [ ] 实现 RAG 服务
- [ ] 实现 API 接口

### 阶段三：前端开发
- [ ] Vue 项目初始化
- [ ] 实现聊天组件
- [ ] 实现知识库管理

### 阶段四：集成测试与部署
- [ ] 联调测试
- [ ] Docker 部署验证
- [ ] 编写使用文档

---

## 11. 验收标准

1. 前端界面正常运行，可发送消息并显示回复
2. 知识库文档上传成功，可被检索
3. RAG 检索返回相关内容
4. AI 回复准确且相关
5. Docker 部署成功，可通过浏览器访问
6. 阿里云服务器可正常运行
