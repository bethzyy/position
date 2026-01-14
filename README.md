# 公司文化及职位解析工具

AI驱动的职业决策辅助工具，帮助求职者全面了解公司文化和职位匹配度。

## 功能特性

### 1. 网页内容抓取
- 支持多个评价网址批量抓取
- 自动处理动态加载内容
- 智能滚动加载所有评论和反馈
- 提取完整的评价内容（包括时间）

### 2. AI智能分析
- **公司文化分析**: 基于员工评价，分析公司氛围、文化、面试流程
- **职位匹配分析**: 结合简历和JD，提供详细的匹配度评估
- **面试准备建议**: 生成针对性的问题清单和回答策略
- **使用GLM-4.6模型**: 稳定可靠的分析能力

### 3. 简历解析
- 支持多种格式: PDF, Word (.doc/.docx), TXT
- 智能提取文本内容
- 自动处理编码问题

### 4. 专业报告生成
- 精美的HTML报告
- 三栏布局：公司文化、职位匹配、面试建议
- 移动端适配
- 支持打印

### 5. 用户友好界面
- 直观的GUI界面
- 参数自动保存
- 实时日志显示
- 进度反馈

## 快速开始

### 环境要求

- Python 3.8+
- Chrome浏览器（用于网页抓取）
- ZHIPU_API_KEY环境变量

### 安装步骤

1. **克隆或下载项目**
   ```bash
   cd C:\D\CAIE_tool\MyAIProduct\position
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **设置API Key**
   ```bash
   # 临时设置（仅当前窗口有效）
   set ZHIPU_API_KEY=your-api-key

   # 永久设置（推荐）
   setx ZHIPU_API_KEY "your-api-key"
   ```

4. **运行程序**
   ```bash
   # 方式1: 双击批处理文件
   启动工具.bat

   # 方式2: 命令行运行
   python main.py
   ```

## 使用指南

### 基本使用流程

1. **输入评价网址**
   - 在"评价网址"框中输入包含员工评价的网页地址
   - 每行一个网址
   - 支持多个网址

2. **选择简历文件**
   - 点击"浏览..."选择简历文件
   - 支持 PDF, Word, TXT 格式

3. **粘贴职位描述**
   - 在"职位描述"框中粘贴完整的JD内容
   - 越详细越好

4. **指定输出路径**
   - 选择生成的HTML报告保存位置
   - 默认: `output/分析报告.html`

5. **开始分析**
   - 点击"开始分析"按钮
   - 等待2-3分钟（取决于网页数量）
   - 分析完成后自动打开报告

### 高级功能

#### 批处理模式
可以在配置文件中预设参数，下次启动自动加载。

配置文件位置: `config.json`

```json
{
  "urls": "https://example.com/review1\nhttps://example.com/review2",
  "resume_path": "C:\\path\\to\\resume.pdf",
  "job_description": "职位描述内容...",
  "output_path": "output/报告.html"
}
```

#### 查看日志
详细的AI调用日志保存在 `logs/` 目录。

文件格式: `ai_calls_YYYYMMDD.log`

日志内容包括:
- 调用时间戳
- 使用的模型
- 输入/输出内容
- Token使用量
- 调用时长

## 项目结构

```
position/
├── main.py                    # GUI主程序
├── web_scraper.py            # 网页抓取模块
├── ai_analyzer.py            # AI分析模块
├── resume_parser.py          # 简历解析模块
├── report_generator.py       # 报告生成模块
├── mhtml_reader.py           # MHTML文件读取模块
├── check_report.py           # 报告检查工具
├── prompts/                  # 提示词模板
│   ├── company_culture_analysis.txt
│   └── position_match_analysis.txt
├── logs/                     # 日志文件目录
├── userdata/                 # 用户数据目录
├── requirements.txt          # 依赖包列表
├── 启动工具.bat              # 启动脚本
├── build_exe.bat             # 构建脚本
├── CLAUDE.md                 # Claude Code 项目指南
└── README.md                 # 本文件
```

**说明:**
- `build/` 和 `dist/` 目录由构建脚本生成，已加入 .gitignore
- `*.spec` 文件是 PyInstaller 自动生成的配置文件，已加入 .gitignore
- 临时文件和构建产物不会被提交到 Git

### .gitignore 配置

项目使用以下 .gitignore 规则：

```
userdata/       # 用户数据目录
dist/           # 构建输出目录
build/          # 构建临时目录
*.spec          # PyInstaller 配置文件
nul             # Windows 空设备文件
```

这样可以确保只提交源代码和配置文件，不包含构建产物和用户数据。

## 技术架构

### 核心模块

1. **WebScraper** - 网页抓取
   - 使用Selenium处理动态内容
   - 智能滚动加载
   - 超时和错误处理
   - 支持 MHTML 格式读取

2. **AIAnalyzer** - AI分析
   - 使用Anthropic兼容接口调用GLM-4.6
   - 完整的日志记录
   - 内容长度自适应

3. **ResumeParser** - 简历解析
   - 多格式支持（PDF/Word/TXT）
   - 编码自动检测

4. **ReportGenerator** - 报告生成
   - Markdown转HTML
   - 精美CSS样式
   - 响应式设计

5. **MHTMLReader** - MHTML读取
   - 支持读取已保存的 MHTML 文件
   - 可离线分析已保存的网页内容

### 技术栈

- **GUI**: Tkinter (Python标准库)
- **网页抓取**: Selenium 4.15+
- **AI接口**: ZhipuAI SDK (GLM-4.6)
- **文档解析**: PyPDF2, python-docx
- **日志**: Python logging
- **构建工具**: PyInstaller

## 测试

### 测试工具

项目包含以下测试工具：

- `check_report.py` - 报告检查工具
- `test_mhtml_read.py` - MHTML 读取测试

### 运行测试

```bash
# 设置API Key
set ZHIPU_API_KEY=your-api-key

# 运行测试
python check_report.py
python test_mhtml_read.py
```

### 测试覆盖

- ✓ 简历解析（TXT/PDF/Word）
- ✓ 报告生成（HTML）
- ✓ AI分析（需要API Key）
- ✓ MHTML 文件读取
- ✓ 网页抓取（需要Chrome）

## 构建可执行程序

### 方法1: 使用构建脚本 (推荐)

#### 步骤1: 环境准备

确保已安装Python 3.8+，然后安装PyInstaller:

```bash
pip install pyinstaller
```

#### 步骤2: 运行构建脚本

```bash
# 在项目根目录运行
build_exe.bat
```

构建脚本会自动:
1. 检查PyInstaller是否安装
2. 清理旧的构建文件
3. 打包所有依赖
4. 生成单个EXE文件

#### 步骤3: 查看输出

构建成功后，可执行文件位于:
```
dist/公司文化职位解析工具.exe
```

文件大小约: **210 MB**

---

### 方法2: 手动构建

如果需要自定义构建参数，可以手动运行PyInstaller:

```bash
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "公司文化职位解析工具" ^
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
```

**参数说明:**

| 参数 | 说明 |
|------|------|
| `--noconfirm` | 覆盖已有文件而不询问 |
| `--onefile` | 打包成单个EXE文件 |
| `--windowed` | 无控制台窗口(GUI程序) |
| `--name` | 指定输出文件名 |
| `--add-data` | 包含prompts文件夹 |
| `--hidden-import` | 显式导入的模块 |
| `--exclude-module` | 排除的模块(避免冲突) |
| `--collect-all` | 收集selenium的所有依赖 |

---

### 构建过程中可能遇到的问题

#### 问题1: Qt绑定冲突

**错误信息:**
```
ERROR: Aborting build process due to attempt to collect multiple Qt bindings packages
```

**解决方案:**
在构建命令中添加排除参数:
```bash
--exclude-module=PyQt5
--exclude-module=PySide6
```

#### 问题2: 文件过大

**原因**: PyInstaller会打包所有依赖，包括不需要的库

**解决方案:**
- 使用 `--exclude-module` 排除不需要的包
- 使用虚拟环境进行构建(只安装必需的依赖)

#### 问题3: 缺少隐藏导入

**错误信息:**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案:**
在构建命令中添加:
```bash
--hidden-import=xxx
```

---

### 构建最佳实践

#### 1. 使用虚拟环境 (推荐)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 只安装必需的依赖
pip install -r requirements.txt
pip install pyinstaller

# 构建
build_exe.bat
```

这样可以显著减小EXE文件大小。

#### 2. 测试EXE文件

构建完成后，在目标机器上测试:

```bash
# 1. 设置API Key
set ZHIPU_API_KEY=your-api-key

# 2. 运行EXE
dist\公司文化职位解析工具.exe

# 3. 测试完整流程
# - 输入网址
# - 选择简历
# - 粘贴JD
# - 运行分析
# - 查看报告
```

#### 3. 分发EXE文件

分发时需要告知用户:
- ✅ Windows 10/11 64位系统
- ✅ 需要安装Chrome浏览器
- ✅ 需要设置ZHIPU_API_KEY环境变量
- ✅ 需要网络连接(调用API和抓取网页)

---

### 构建输出目录说明

```
position/
├── build/                      # 构建临时文件（已加入 .gitignore）
│   └── 公司文化职位解析工具/
│       ├── Analysis-00.toc    # 分析文件
│       ├── EXE-00.toc         # EXE文件表
│       ├── PKG-00.toc         # 包文件表
│       ├── PYZ-00.pyz         # Python归档
│       ├── warn-*.txt         # 警告信息
│       ├── xref-*.html        # 依赖关系图
│       └── *.pkg              # PyInstaller中间打包文件（约220MB）
├── dist/                       # 最终输出（已加入 .gitignore）
│   └── 公司文化职位解析工具.exe  ← 可执行文件
└── *.spec                      # PyInstaller配置文件（已加入 .gitignore）
```

**注意:**
- `build/` 和 `dist/` 目录会在每次构建时重新生成
- `.pkg` 文件是 PyInstaller 的中间打包文件，用于生成最终的 .exe
- 这些目录和文件已加入 .gitignore，不会被提交到 Git

---

### 使用EXE文件

#### 运行要求

- **操作系统**: Windows 10/11 (64位)
- **浏览器**: Chrome (用于网页抓取)
- **环境变量**: `ZHIPU_API_KEY`
- **网络**: 互联网连接

#### 运行方式

**方式1: 双击运行**
```
直接双击 dist/公司文化职位解析工具.exe
```

**方式2: 命令行运行**
```bash
cd dist
公司文化职位解析工具.exe
```

**方式3: 创建快捷方式**
1. 右键 `公司文化职位解析工具.exe`
2. 选择"发送到" -> "桌面快捷方式"
3. 以后可以直接从桌面启动

#### 首次运行

首次运行时，EXE会自动解压到临时目录，可能需要1-2分钟。之后的启动会快很多。

---

### EXE vs 源代码对比

| 特性 | EXE版本 | 源代码版本 |
|------|---------|-----------|
| 安装Python | ❌ 不需要 | ✅ 需要 |
| 安装依赖 | ❌ 不需要 | ✅ 需要 |
| 文件大小 | 210 MB | 几MB |
| 便携性 | ✅ 高 | ❌ 低 |
| 可修改性 | ❌ 不可修改 | ✅ 可修改 |
| 调试难度 | ❌ 困难 | ✅ 容易 |

**推荐:**
- **个人使用**: EXE版本
- **开发/调试**: 源代码版本
- **分发给他人**: EXE版本

## 常见问题

### 1. Chrome驱动问题

**问题**: WebDriver初始化失败

**解决**:
- 确保已安装Chrome浏览器
- 程序会自动下载对应的ChromeDriver
- 如果失败，手动安装ChromeDriver

### 2. API Key错误

**问题**: 提示未找到ZHIPU_API_KEY

**解决**:
```bash
# 检查是否设置
echo %ZHIPU_API_KEY%

# 重新设置
set ZHIPU_API_KEY=your-api-key

# 永久设置
setx ZHIPU_API_KEY "your-api-key"
```

### 3. 网页抓取失败

**问题**: 某些网页无法抓取

**解决**:
- 检查网址是否正确
- 某些网站可能有反爬机制
- 尝试使用其他类似的网站

### 4. AI分析超时

**问题**: AI调用时间过长

**解决**:
- 正常情况下30-60秒
- 检查网络连接
- 查看日志文件了解详情

### 5. 内存不足

**问题**: 处理大量内容时内存不足

**解决**:
- 程序会自动截断过长的内容
- 关闭其他占用内存的程序
- 增加系统内存

## 性能参考

- 简历解析: < 1秒
- 单个网页抓取: 10-30秒
- AI分析: 30-60秒/次
- 报告生成: < 1秒
- **总流程**: 2-3分钟

## 注意事项

### API使用

- 使用GLM-4.6模型（稳定）
- 每次分析约消耗3000-5000 tokens
- 请确保API账户有足够余额

### 隐私保护

- 所有数据仅用于AI分析
- 不会上传到除GLM API外的服务器
- 本地日志文件包含完整数据，注意保护

### 内容质量

- AI分析结果仅供参考
- 建议结合其他信息源
- 最终决策请自行判断

## 更新日志

### v1.6 (2026-01-12)
- ✓ 实现 MHTML 文件读取功能
- ✓ 支持离线分析已保存的网页
- ✓ 优化用户界面
- ✓ 添加配置持久化

### v1.5 (2026-01-12)
- ✓ 添加文件夹选择功能
- ✓ 改进文件处理流程

### v1.4 (2026-01-12)
- ✓ 添加 MHTML 功能
- ✓ 改进网页抓取稳定性

### v1.0 (2026-01-12)
- ✓ 实现所有核心功能
- ✓ 网页抓取支持动态内容
- ✓ AI分析使用GLM-4.6
- ✓ 简历解析多格式支持
- ✓ HTML报告生成
- ✓ GUI界面
- ✓ 参数持久化
- ✓ 完整日志记录
- ✓ 测试套件

## 许可证

本项目为CAIE AI实战训练营教学项目。

## 联系方式

如有问题或建议，请通过以下方式联系:
- 项目路径: `C:\D\CAIE_tool\MyAIProduct\position`
- 查看 CLAUDE.md 了解项目配置和开发指南
- 查看 MHTML功能使用说明.md 了解 MHTML 功能
- 查看各种 EXE更新报告 了解版本更新详情

---

**🤖 Generated with AI Assistance**

CAIE AI实战训练营 - 2026
