@echo off
chcp 65001 >nul
echo ========================================
echo 批量处理工具 - EXE构建脚本
echo ========================================
echo.

REM 检查并安装PyInstaller
echo [1/3] 检查PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller已安装
)

echo.
echo [2/3] 开始构建EXE...
echo.

REM 删除旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 构建EXE
python -m PyInstaller --noconfirm --onefile --windowed --name "批量职位解析工具" ^
    --add-data "prompts2;prompts2" ^
    --add-data "prompts;prompts" ^
    --hidden-import=anthropic ^
    --hidden-import=PyPDF2 ^
    --hidden-import=docx ^
    --hidden-import=openpyxl ^
    --exclude-module=PyQt5 ^
    --exclude-module=PySide6 ^
    --exclude-module=matplotlib ^
    --exclude-module=IPython ^
    --exclude-module=pygame ^
    batch_tool_main.py

if errorlevel 1 (
    echo.
    echo [X] 构建失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 构建成功！
echo.
echo ========================================
echo EXE文件位置: dist\批量职位解析工具.exe
echo ========================================
echo.
pause
