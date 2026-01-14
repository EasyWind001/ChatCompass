FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV STORAGE_TYPE=elasticsearch

# 暴露端口（用于未来的Web UI）
EXPOSE 8000

# 启动命令（在docker-compose中覆盖）
CMD ["python", "main.py"]
