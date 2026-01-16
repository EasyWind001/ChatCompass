#!/bin/bash
set -e

echo "=========================================="
echo "ChatCompass 启动中..."
echo "=========================================="
echo ""

# 等待Elasticsearch就绪
echo "[1/3] 等待Elasticsearch就绪..."
MAX_RETRY=30
RETRY=0
until curl -s http://elasticsearch:9200/_cluster/health >/dev/null 2>&1; do
    RETRY=$((RETRY+1))
    if [ $RETRY -ge $MAX_RETRY ]; then
        echo "  ❌ Elasticsearch启动超时！"
        exit 1
    fi
    echo "  等待Elasticsearch启动... ($RETRY/$MAX_RETRY)"
    sleep 2
done
echo "  ✅ Elasticsearch已就绪"
echo ""

# 安装Playwright浏览器
echo "[2/3] 检查Playwright浏览器..."
CHROMIUM_PATH="/root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome"

if [ -f "$CHROMIUM_PATH" ]; then
    echo "  ✅ Chromium已安装"
else
    echo "  📦 安装Chromium浏览器（首次运行需要几分钟）..."
    echo "  提示：下载约100MB，请耐心等待..."
    
    # 尝试安装浏览器
    if playwright install chromium; then
        echo "  ✅ Chromium安装成功"
    else
        echo "  ⚠️  Chromium安装失败，尝试安装依赖..."
        if playwright install-deps chromium && playwright install chromium; then
            echo "  ✅ Chromium安装成功（第二次尝试）"
        else
            echo "  ❌ Chromium安装失败！"
            echo "  提示：请检查网络连接或手动安装："
            echo "    docker exec -it chatcompass_app playwright install chromium"
            echo "  ChatCompass将继续运行，但无法抓取ChatGPT对话。"
        fi
    fi
fi
echo ""

# 下载Ollama模型（可选）
echo "[3/3] 检查Ollama模型..."
if curl -s http://ollama:11434/api/tags >/dev/null 2>&1; then
    echo "  检测到Ollama服务，下载qwen2.5:3b模型..."
    if curl -X POST http://ollama:11434/api/pull -d '{"name":"qwen2.5:3b"}' 2>/dev/null; then
        echo "  ✅ Ollama模型就绪"
    else
        echo "  ⚠️  Ollama模型下载失败（可忽略）"
    fi
else
    echo "  ℹ️  Ollama服务未启动（可忽略）"
fi
echo ""

echo "=========================================="
echo "🎉 ChatCompass启动完成！"
echo "=========================================="
echo ""
echo "使用方法："
echo "  docker exec -it chatcompass_app python main.py"
echo ""
echo "如果Playwright安装失败，请手动执行："
echo "  docker exec -it chatcompass_app playwright install chromium"
echo ""
echo "容器保持运行中..."
echo ""

# 保持容器运行
tail -f /dev/null
