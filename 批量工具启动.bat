@echo off
chcp 65001 >nul
echo ========================================
echo 批量公司文化职位解析工具
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查环境变量
echo [1/3] 检查环境变量...
if not defined ZHIPU_API_KEY (
    echo 警告: 未设置ZHIPU_API_KEY环境变量
    echo 请先设置: set ZHIPU_API_KEY=你的API密钥
    echo.
    set /p ZHIPU_API_KEY="请输入你的智谱AI API密钥: "
)

REM 检查依赖
echo [2/3] 检查依赖...
python -c "import anthropic" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install anthropic PyPDF2 python-docx openpyxl
)

REM 启动程序
echo [3/3] 启动程序...
echo.
python batch_tool_main.py

if errorlevel 1 (
    echo.
    echo 程序异常退出
    pause
)
