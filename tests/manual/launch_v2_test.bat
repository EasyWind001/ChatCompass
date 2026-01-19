@echo off
chcp 65001 >nul
echo ============================================================
echo ChatCompass V2 UI 测试启动器
echo ============================================================
echo.
echo 选择测试模式:
echo   1. 代码验证（快速检查）
echo   2. UI演示（手动测试）
echo   3. 自动化测试（无需GUI）
echo.
set /p choice="请选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 正在运行代码验证...
    python ui_validation_v2.py
) else if "%choice%"=="2" (
    echo.
    echo 正在启动UI演示...
    echo 提示: 测试以下功能
    echo   - Ctrl+F: 搜索
    echo   - Esc: 清除
    echo   - Ctrl+G: 切换视图
    echo   - 点击按钮测试交互
    echo.
    python test_modern_ui_v2.py
) else if "%choice%"=="3" (
    echo.
    echo 正在运行自动化测试...
    echo 注意: 将打开GUI窗口自动测试
    python ui_automation_v2_test.py
) else (
    echo 无效选择
)

echo.
pause
