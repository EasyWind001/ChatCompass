#!/bin/bash
# ChatCompass 快速启动脚本

# 激活虚拟环境
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "[警告] 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 运行程序
python main.py "$@"
