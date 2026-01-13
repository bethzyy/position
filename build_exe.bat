@echo off
chcp 65001 >nul
title 构建可执行程序

echo ========================================
echo 构建可执行程序
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

REM 检查PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/4] 安装PyInstaller...
    pip install pyinstaller
) else (
    echo [1/4] PyInstaller已安装
)

echo [2/4] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [3/4] 开始构建...
echo.

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "公司文化职位解析工具" ^
    --icon=NONE ^
    --add-data "prompts;prompts" ^
    --hidden-import=selenium ^
    --hidden-import=anthropic ^
    --hidden-import=PyPDF2 ^
    --hidden-import=docx ^
    --exclude-module=PyQt5 ^
    --exclude-module=PySide6 ^
    --exclude-module=matplotlib ^
    --exclude-module=IPython ^
    --exclude-module=pygame ^
    --collect-all selenium ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    pause
    exit /b 1
)

echo.
echo [4/4] 构建完成！
echo.
echo 可执行文件位置: dist\公司文化职位解析工具.exe
echo.

REM 复制必要文件到dist目录
echo 复制配置文件...
copy config.json dist\ >nul 2>&1

echo.
echo ========================================
echo 构建成功！
echo ========================================
echo.
echo 输出文件: dist\公司文化职位解析工具.exe
echo.
echo 使用说明:
echo 1. 确保设置了ZHIPU_API_KEY环境变量
echo 2. 双击运行exe文件
echo.

pause
