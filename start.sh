#!/bin/bash

# AI 智能客服系统 - 快速启动脚本（本地开发）
# 使用 Docker Compose 一键启动所有服务

set -e

echo "========================================="
echo "AI 智能客服系统 - 快速启动"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env 文件不存在，从 .env.example 创建...${NC}"
    cp .env.example .env
    echo -e "${RED}请编辑 .env 文件配置 DASHSCOPE_API_KEY${NC}"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误：Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装（支持新旧命令）
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误：Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

# 设置 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# 停止旧服务
echo -e "${YELLOW}停止旧服务...${NC}"
$COMPOSE_CMD down 2>/dev/null || true

# 构建并启动
echo -e "${YELLOW}构建并启动服务...${NC}"
$COMPOSE_CMD up -d --build

# 等待服务启动
echo -e "${YELLOW}等待服务启动（约 15 秒）...${NC}"
sleep 5

# 检查服务状态
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "访问地址：http://localhost"
echo ""
echo "常用命令:"
echo "  查看日志：$COMPOSE_CMD logs -f"
echo "  停止服务：$COMPOSE_CMD down"
echo "  重启服务：$COMPOSE_CMD restart"
echo ""
