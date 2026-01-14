#!/bin/bash

# ChatCompass Docker 启动脚本

set -e

echo "================================"
echo " ChatCompass Docker 启动脚本"
echo "================================"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] 未检测到Docker，请先安装Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "[1/5] 检查Docker服务..."
if ! docker ps &> /dev/null; then
    echo "[错误] Docker服务未启动，请先启动Docker服务"
    exit 1
fi
echo "✓ Docker服务正常"

echo ""
echo "[2/5] 拉取所需镜像..."
docker-compose pull

echo ""
echo "[3/5] 构建ChatCompass应用..."
docker-compose build

echo ""
echo "[4/5] 启动所有服务..."
docker-compose up -d

echo ""
echo "[5/5] 等待服务就绪..."
sleep 10

echo ""
echo "================================"
echo " 服务启动完成！"
echo "================================"
echo ""
echo "📊 Elasticsearch: http://localhost:9200"
echo "🤖 Ollama:        http://localhost:11434"
echo "💬 ChatCompass:   正在运行（CLI模式）"
echo ""
echo "💡 使用命令:"
echo "   docker-compose logs -f chatcompass  # 查看日志"
echo "   docker-compose down                 # 停止服务"
echo "   docker exec -it chatcompass-app python main.py  # 进入CLI"
echo ""
echo "首次启动需要下载Ollama模型（约3GB），请耐心等待..."
echo "可以使用 'docker-compose logs -f ollama' 查看下载进度"
echo ""
