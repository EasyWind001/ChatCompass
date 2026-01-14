@echo off
REM ChatCompass Windows 安装脚本

echo ========================================
echo ChatCompass 安装程序
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检测到Python版本:
python --version
echo.

REM 创建虚拟环境
echo [2/4] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo 虚拟环境创建成功
echo.

REM 激活虚拟环境
echo [3/4] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [4/4] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo.

REM 安装Playwright浏览器
echo [额外] 安装Playwright浏览器...
playwright install chromium
echo.

REM 复制配置文件
if not exist .env (
    echo [配置] 创建配置文件...
    copy .env.example .env
    echo 请编辑 .env 文件配置AI模式
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 激活虚拟环境: venv\Scripts\activate
echo   2. 运行程序: python main.py
echo.
echo 或直接运行: run.bat
echo.
pause
