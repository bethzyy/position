@echo off
chcp 65001 >nul
echo ========================================
echo 批量处理工具 - EXE构建脚本
echo ========================================
echo.

REM 检查PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo 开始构建EXE...
echo.

REM 构建EXE
pyinstaller --noconfirm --onefile --windowed --name "批量职位解析工具" ^
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
    echo 构建失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建成功！
echo ========================================
echo.
echo EXE文件位置: dist\批量职位解析工具.exe
echo.

REM 复制配置文件
echo 复制配置文件到dist目录...
copy /Y batch_config.json dist\ >nul 2>&1
copy /Y 批量工具README.md dist\ >nul 2>&1

echo.
echo 完成！
echo.
pause
