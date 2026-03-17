# AI 智能客服系统 - 部署指南

本文档详细说明如何将 AI 智能客服系统部署到阿里云 Linux 服务器。

## 一、服务器准备

### 1.1 服务器配置要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2 核 | 4 核 |
| 内存 | 2GB | 4GB |
| 存储 | 20GB | 40GB SSD |
| 操作系统 | Alibaba Cloud Linux 3 / CentOS 7+ / Ubuntu 20.04+ |

### 1.2 开放安全组端口

登录阿里云控制台，进入 ECS 实例管理：

1. 找到你的实例，点击「安全组」
2. 点击「配置规则」
3. 添加入方向规则：
   - 端口范围：80/80 (HTTP)
   - 授权对象：0.0.0.0/0
   - 协议：TCP

## 二、环境安装

### 2.1 连接服务器

```bash
# 使用 SSH 连接
ssh root@your-server-ip
```

### 2.2 安装 Docker

**方式一：使用官方脚本（推荐）**

```bash
curl -fsSL https://get.docker.com | bash -s docker
systemctl start docker
systemctl enable docker
```

**方式二：手动安装（CentOS/Alibaba Cloud Linux）**

```bash
# 卸载旧版本（如果有）
sudo yum remove -y docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine

# 安装 yum 工具包
sudo yum install -y yum-utils

# 添加 Docker 官方仓库
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker 引擎
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 2.3 配置 Docker 镜像加速器（可选，加速下载）

```bash
# 创建配置文件
sudo mkdir -p /etc/docker

# 配置镜像加速（使用阿里云镜像）
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.cn-hangzhou.aliyuncs.com"
  ]
}
EOF

# 重载配置并重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 三、项目部署

### 3.1 上传项目文件

**方式一：使用 SCP**

在本地计算机执行：

```bash
# 上传整个项目
scp -r . root@your-server-ip:/opt/aics/

# 或者使用 rsync（支持断点续传）
rsync -avz --progress . root@your-server-ip:/opt/aics/
```

**方式二：使用 Git**

```bash
# 在服务器上执行
cd /opt
git clone <your-repo-url> aics
cd aics
```

**方式三：使用 FTP/SFTP 工具**

- FileZilla
- WinSCP
- Xftp

### 3.2 配置环境变量

```bash
cd /opt/aics

# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

编辑 `.env` 文件：

```bash
# 阿里云百炼 API Key（必填）
DASHSCOPE_API_KEY=sk-your-actual-api-key

# Flask 密钥（建议修改）
FLASK_SECRET_KEY=your-random-secret-key-xyz123

# 其他配置保持默认即可
FLASK_ENV=production
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000
```

### 3.3 启动服务

**方式一：使用 deploy.sh 脚本（自动安装 Docker 和 Docker Compose）**

```bash
cd /opt/aics

# 赋予执行权限
chmod +x deploy.sh

# 执行部署（自动检测并安装依赖）
sudo ./deploy.sh
```

**方式二：使用 start.sh 脚本（需要预先安装 Docker）**

```bash
cd /opt/aics
chmod +x start.sh
./start.sh
```

**方式三：手动使用 docker-compose 启动**

```bash
cd /opt/aics

# 构建并启动所有服务
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f
```

### 3.4 验证部署

```bash
# 查看容器状态
docker-compose ps

# 应该看到 3 个运行中的容器：
# NAME            SERVICE     STATUS
# ai-backend-1    backend     Up
# ai-frontend-1   frontend    Up
# ai-nginx-1      nginx       Up
```

## 四、访问应用

### 4.1 浏览器访问

打开浏览器，访问：

```
http://your-server-ip
```

### 4.2 测试功能

1. **聊天功能**：在聊天框输入消息，确认能收到 AI 回复
2. **知识库上传**：上传一个 txt 测试文件
3. **RAG 检索**：询问与上传文档相关的问题

## 五、日常运维

### 5.1 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### 5.2 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
```

### 5.3 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用，会删除 ChromaDB 数据）
docker-compose down -v
```

### 5.4 更新项目

```bash
cd /opt/aics

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 5.5 备份数据

```bash
# 备份 ChromaDB 数据卷
docker run --rm \
    -v ai_chroma_data:/source \
    -v $(pwd):/backup \
    alpine tar czf /backup/chroma_backup.tar.gz -C /source .

# 恢复数据
docker run --rm \
    -v ai_chroma_data:/target \
    -v $(pwd):/backup \
    alpine tar xzf /backup/chroma_backup.tar.gz -C /target
```

## 六、故障排查

### 6.1 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看具体错误
docker-compose logs backend

# 常见错误：
# 1. 端口占用：修改 docker-compose.yml 端口
# 2. 内存不足：检查服务器资源
# 3. API Key 无效：检查.env 配置
```

### 6.2 无法访问网页

```bash
# 检查防火墙
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --reload

# 检查安全组
# 登录阿里云控制台确认 80 端口已开放

# 检查 Nginx 配置
docker-compose exec nginx nginx -t
```

### 6.3 前端访问正常但 API 失败

```bash
# 检查后端服务状态
docker-compose ps backend

# 查看后端日志
docker-compose logs backend

# 测试后端直接访问
docker-compose exec backend curl http://localhost:5000/api/health

# 检查 nginx 到后端的连接
docker-compose exec nginx nginx -T | grep upstream
```

### 6.4 AI 回复失败

```bash
# 检查 API Key
docker-compose exec backend env | grep DASHSCOPE

# 测试 API 连通性
docker-compose exec backend curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "test", "session_id": "test"}' \
    http://localhost:5000/api/chat
```

## 七、性能优化

### 7.1 配置 Nginx 日志轮转

编辑 `nginx.conf`，添加日志配置：

```nginx
http {
    # ... 其他配置 ...

    access_log /var/log/nginx/access.log main buffer=16k flush=1m;
    error_log /var/log/nginx/error.log warn;
}
```

### 7.2 配置 HTTPS（推荐）

使用 Certbot 配置免费 SSL 证书：

```bash
# 安装 Certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 0 1 * * certbot renew --quiet
```

## 八、监控告警

### 8.1 配置 Docker 日志限制

编辑 `/etc/docker/daemon.json`：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 8.2 服务健康检查

```bash
# 检查所有容器状态
docker-compose ps

# 检查后端健康状态
curl http://localhost:5000/health

# 检查前端访问
curl http://localhost
```

## 九、常见问题

### Q1: 首次构建很慢

使用国内镜像源：
- 修改 `Dockerfile.frontend` 和 `Dockerfile.backend` 使用国内镜像源
- 配置 Docker 镜像加速器（见 2.3 节）

### Q2: 上传文件失败

检查 `nginx.conf` 中的 `client_max_body_size` 配置（默认 50M）。

### Q3: 对话历史丢失

ChromaDB 数据存储在 Docker 持久化卷中，确保不要随意执行 `docker-compose down -v`。

### Q4: nginx 启动失败

检查 nginx.conf 配置是否正确：
```bash
docker-compose exec nginx nginx -t
```

---

**技术支持**: 如有问题，请查看项目 README.md 或提交 Issue。
