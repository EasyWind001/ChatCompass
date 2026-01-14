@echo off
REM ChatCompass 快速启动脚本

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [警告] 虚拟环境不存在，请先运行 install.bat
    pause
    exit /b 1
)

REM 运行程序
python main.py %*
