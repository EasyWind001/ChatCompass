#!/bin/bash
# ChatCompass Linux/macOS 安装脚本

echo "========================================"
echo "ChatCompass 安装程序"
echo "========================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.9+"
    exit 1
fi

echo "[1/4] 检测到Python版本:"
python3 --version
echo

# 创建虚拟环境
echo "[2/4] 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[错误] 虚拟环境创建失败"
    exit 1
fi
echo "虚拟环境创建成功"
echo

# 激活虚拟环境
echo "[3/4] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[4/4] 安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi
echo

# 安装Playwright浏览器
echo "[额外] 安装Playwright浏览器..."
playwright install chromium
echo

# 复制配置文件
if [ ! -f .env ]; then
    echo "[配置] 创建配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置AI模式"
fi

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "使用方法:"
echo "  1. 激活虚拟环境: source venv/bin/activate"
echo "  2. 运行程序: python main.py"
echo
echo "或直接运行: ./run.sh"
echo

# 添加执行权限
chmod +x run.sh
