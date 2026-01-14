@echo off
REM Windows批处理脚本 - 运行测试

echo ========================================
echo ChatCompass 测试套件
echo ========================================
echo.

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 运行测试
python run_tests.py %*

pause
