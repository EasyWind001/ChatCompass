@echo off
chcp 65001 >nul
echo ================================
echo  ChatCompass Docker 启动脚本
echo ================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Docker，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [1/5] 检查Docker服务...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker服务未启动，请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✓ Docker服务正常

echo.
echo [2/5] 拉取所需镜像...
docker-compose pull

echo.
echo [3/5] 构建ChatCompass应用...
docker-compose build

echo.
echo [4/5] 启动所有服务...
docker-compose up -d

echo.
echo [5/5] 等待服务就绪...
timeout /t 10 /nobreak >nul

echo.
echo ================================
echo  服务启动完成！
echo ================================
echo.
echo 📊 Elasticsearch: http://localhost:9200
echo 🤖 Ollama:        http://localhost:11434
echo 💬 ChatCompass:   正在运行（CLI模式）
echo.
echo 💡 使用命令:
echo    docker-compose logs -f chatcompass  # 查看日志
echo    docker-compose down                 # 停止服务
echo    docker exec -it chatcompass-app python main.py  # 进入CLI
echo.
echo 首次启动需要下载Ollama模型（约3GB），请耐心等待...
echo 可以使用 "docker-compose logs -f ollama" 查看下载进度
echo.
pause
