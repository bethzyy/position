@echo off
chcp 65001 >nul
title 公司文化及职位解析工具

echo ========================================
echo 公司文化及职位解析工具
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺少依赖，正在安装...
    pip install -r requirements.txt
)

echo [2/3] 检查API Key...
if "%ZHIPU_API_KEY%"=="" (
    echo [警告] 未设置ZHIPU_API_KEY环境变量
    echo.
    echo 请先设置API Key:
    echo set ZHIPU_API_KEY=your-api-key
    echo.
    echo 或者以管理员身份运行:
    echo setx ZHIPU_API_KEY "your-api-key"
    echo.
    pause
)

echo [3/3] 启动程序...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
)
