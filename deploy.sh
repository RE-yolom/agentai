#!/bin/bash

# AI 智能客服系统 - 部署脚本
# 用于阿里云 Linux 服务器
# 自动安装 Docker 并启动服务

set -e

echo "========================================="
echo "AI 智能客服系统 - 部署脚本"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请使用 sudo 运行此脚本${NC}"
  exit 1
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

echo -e "${YELLOW}检测到操作系统：$OS${NC}"

# 安装 Docker
install_docker() {
    echo -e "${YELLOW}安装 Docker...${NC}"

    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y ca-certificates curl gnupg
            install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            chmod a+r /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        centos|alinux|almalinux|rocky)
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        *)
            # 尝试使用官方脚本
            curl -fsSL https://get.docker.com | bash
            ;;
    esac

    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}Docker 安装完成${NC}"
}

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    install_docker
fi

# 检查 Docker Compose 是否安装（支持新旧命令）
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Docker Compose 未安装，开始安装...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose 安装完成${NC}"
fi

# 设置 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# 获取项目目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}当前目录：$(pwd)${NC}"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env 文件不存在，从 .env.example 创建...${NC}"
    cp .env.example .env
    echo -e "${RED}请编辑 .env 文件配置 DASHSCOPE_API_KEY${NC}"
    echo "按任意键继续..."
    read -n 1 -s
fi

# 停止旧服务
echo -e "${YELLOW}停止旧服务...${NC}"
$COMPOSE_CMD down 2>/dev/null || true

# 构建并启动
echo -e "${YELLOW}构建并启动服务...${NC}"
$COMPOSE_CMD up -d --build

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
$COMPOSE_CMD ps

# 显示访问地址
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
echo ""
echo "========================================="
echo -e "${GREEN}部署完成!${NC}"
echo "========================================="
echo "访问地址：http://${SERVER_IP}"
echo ""
echo "查看日志：$COMPOSE_CMD logs -f"
echo "停止服务：$COMPOSE_CMD down"
echo "重启服务：$COMPOSE_CMD restart"
echo "========================================="
