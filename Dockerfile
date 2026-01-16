FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括Playwright所需的浏览器依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libjpeg62-turbo \
    libpng16-16 \
    libvpx6 \
    libwebp6 \
    libopus0 \
    libharfbuzz0b \
    libenchant-2-2 \
    libsecret-1-0 \
    libhyphen0 \
    libgles2 \
    gstreamer1.0-libav \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器（重要！）
# 注意：如果构建时网络不稳定，可以注释掉这两行，在运行时由entrypoint安装
RUN playwright install chromium --with-deps || echo "⚠️  Playwright安装失败，将在运行时安装"

# 复制应用代码和启动脚本
COPY . .
COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV STORAGE_TYPE=elasticsearch

# 暴露端口（用于未来的Web UI）
EXPOSE 8000

# 启动命令（在docker-compose中覆盖）
CMD ["/docker_entrypoint.sh"]
